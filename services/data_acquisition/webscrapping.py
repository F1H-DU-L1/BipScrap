import os
import csv
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import requests
from selenium.webdriver.common.by import By

import psycopg2
from psycopg2 import sql

import json
import pika
from dotenv import load_dotenv
import schedule

from io import BytesIO
from docx import Document
from PyPDF2 import PdfReader

# Konfiguracja Selenium
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Tryb bez GUI
chrome_options.add_argument("--no-sandbox")  # Ważne dla kontenerów
chrome_options.add_argument("--disable-dev-shm-usage")  # Zapobiega problemom z pamięcią
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")

# Ustawienie ścieżki do ChromeDriver
service = Service("/usr/local/bin/chromedriver")

load_dotenv(override=True)
# Ścieżka do folderu, w którym będą zapisywane pobrane pliki
# UWAGA - zmienić dla właściwego środowiska
download_dir = os.getenv("DIRECTORY_DIR")

# Konfiguracja preferencji pobierania
prefs = {'download.default_directory': download_dir }
chrome_options.add_experimental_option('prefs', prefs)

driver = webdriver.Chrome(service=service, options=chrome_options) # <- do uruchamiania w dockerze
# driver = webdriver.Chrome(options=chrome_options) # <- do uruchamiania lokalnego

VISITED = set()
HEADERS = {"User-Agent": "Mozilla/5.0"}

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
DATABASE_URL = os.getenv("DATABASE_URL")
MAX_PAGES = os.getenv("MAX_PAGES")
DATA_MANAGEMENT_HOST = os.getenv("DATA_MANAGEMENT_HOST")
DATA_MANAGEMENT_PORT = os.getenv("DATA_MANAGEMENT_PORT")


def insert_to_db(base_url, timestamp, url, content):

    data = {
        "base_url": base_url,
        "scrap_datetime": timestamp,
        "url": url,
        "content": content
    }
    #response = requests.post(DATABASE_URL + "/fulldoc", json=data)
    response = requests.post(f"http://{DATA_MANAGEMENT_HOST}:{DATA_MANAGEMENT_PORT}/fulldoc", json=data)

    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Error:", response.status_code, response.text)


def extract_text_from_file(file_url):
    """Pobiera plik (PDF, DOCX) i wyciąga z niego tekst. Czeka 10 sekund na pobranie pliku."""
    try:
        # Sprawdzanie czy plik jest zapisany w folderze /files
        filename = file_url.split("/")[-1]
        file_path = os.path.join(download_dir, filename)
        
        # Poczekaj maksymalnie 10 sekund, aż plik zostanie pobrany
        for _ in range(10):
            if os.path.exists(file_path):
                break
            time.sleep(1)  # Sprawdzaj co sekundę

        if os.path.exists(file_path):
            print(f"📄 Plik pobrany: {file_path}")
            
            # Odczytaj zawartość pliku
            file_ext = filename.split('.')[-1].lower()
            text = ""

            if file_ext == "pdf":
                # Odczytywanie PDF
                with open(file_path, "rb") as f:
                    reader = PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text
            elif file_ext == "docx":
                # Odczytywanie DOCX
                with open(file_path, "rb") as f:
                    doc = Document(f)
                    text = '\n'.join([para.text for para in doc.paragraphs])
            else:
                print(f"⚠️ Nieobsługiwany typ pliku: {file_ext}")

            # Usuwanie pliku po przetworzeniu
            os.remove(file_path)
            print(f"✅ Plik {file_path} został przetworzony i usunięty.")
            return text.strip()
        else:
            print(f"⚠️ Plik {file_path} nie został pobrany w ciągu 10 sekund.")
            return None
    except Exception as e:
        print(f"❌ Błąd podczas pobierania lub przetwarzania pliku {file_url}: {e}")
        return None


def send_to_rabbitmq(base_url, timestamp, url):
    """Wysyła url i wyczyszczoną zawartość do kolejki rabbitmq"""
    # Connect
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
    channel = connection.channel()

    # Queue declare
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

    # Prepare message
    message = json.dumps({"base_url": base_url, "timestamp": timestamp, "url": url})

    # Send to queue
    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ_QUEUE,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f"[x] Wysłano do kolejki: {message}")
    connection.close()

def get_soup_selenium(url):
    """Pobiera stronę przy użyciu Selenium (dla JS i nie tylko)."""
    try:
        driver.get(url)
        # Czekamy na załadowanie elementów strony
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))

        # Można dodać przewijanie strony, aby załadować wszystkie elementy
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Czekamy na załadowanie JS

        print(f"🔄 Załadowano stronę: {url}")  # Debugging
        return BeautifulSoup(driver.page_source, "html.parser"), driver.page_source
    except Exception as e:
        print(f"❌ Błąd przy pobieraniu strony {url}: {e}")
        return None, None

def extract_main_content(soup):
    """Usuwa nagłówek, stopkę, menu, head, paski nawigacyjne i inne zbędne elementy ze strony."""

    # Usuwamy niechciane tagi w BeautifulSoup
    for tag in soup.find_all(["header", "footer", "nav", "aside", "head", "script", "style"]):
        tag.decompose()

    # Czyszczenie treści strony
    cleaned_content = soup.get_text(strip=True)

    return cleaned_content

def crawl(domain, base_url, max_pages_per_url=None):
    """Przeszukuje całą domenę i zbiera dane z podstron oraz plików PDF, DOCX."""
    queue = [base_url]
    visited = set()
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    while queue:
        url = queue.pop(0)

        # Jeżeli osiągnięto limit, przerywamy dalsze przetwarzanie tego URL
        if max_pages_per_url and len(visited) >= max_pages_per_url:
            print(f"🔒 Osiągnięto limit przetworzonych stron ({max_pages_per_url}) na URL: {base_url}")
            break

        if url in visited:
            continue

        visited.add(url)
        print(f"🔍 Przetwarzanie: {url}")

        # Pobieranie strony przy użyciu Selenium
        soup, raw_html = get_soup_selenium(url)
        if not soup or not raw_html:
            print(f"❌ Błąd podczas przetwarzania strony {url}")
            continue

        # Czyszczenie treści
        content = extract_main_content(soup)

        # Zapisywanie wyników TODO baza danych

        insert_to_db(base_url, timestamp, url, content)
        send_to_rabbitmq(base_url, timestamp, url)
        print(f"📄 Zapisano stronę: {url}")

        # Szukanie kolejnych podstron
        links_to_visit = []
        for link in soup.find_all("a", href=True):
            full_url = urljoin(url, link["href"])
            parsed_url = urlparse(full_url)

            if parsed_url.netloc == urlparse(base_url).netloc and full_url not in visited:
                # Sprawdzamy czy link to plik PDF lub DOCX
                if any(full_url.lower().endswith(ext) for ext in ['.pdf', '.docx']):
                    visited.add(full_url)
                    print(f"📄 Znaleziono plik: {full_url}")
                    # Otwieramy url pliku
                    driver.get(full_url)
                    file_text = extract_text_from_file(full_url)

                    if file_text:
                        # Można dodać zapisywanie lub wysyłanie do RabbitMQ
                        send_to_rabbitmq(base_url, timestamp, url)
                        insert_to_db(base_url, timestamp, url, content)
                        print(f"📄 Zapisano plik: {full_url}")
                    else:
                        print(f"⚠️ Nie udało się odczytać pliku: {full_url}")
                else:
                    # Pomiń pliki .doc
                    if not full_url.lower().endswith('.doc'):
                        links_to_visit.append(full_url)

        # Debugging: Sprawdzamy, czy są linki do odwiedzenia
        # if links_to_visit:
        #     print(f"🔗 Zebrane linki do odwiedzenia: {links_to_visit}")
        # else:
        #     print(f"🔗 Brak linków do odwiedzenia na stronie {url}")

        # Przetwarzanie linków na stronie (kliknięcie w linki)
        for next_url in links_to_visit:
            if next_url not in visited:
                # print(f"🔗 Dodawanie podstrony: {next_url}")
                queue.append(next_url)

        time.sleep(1)  # Unikanie przeciążenia serwera

def main():
    """Główna funkcja uruchamiająca skrypt."""
    with open("./urls.txt", "r") as file:
        urls = [line.strip() for line in file if line.strip() != ""]
    
    max_pages_per_url = MAX_PAGES  # Limit podstron, np. 15. Można ustawić na None, aby nie było limitu.

    for url in urls:
        print(f"🌍 Skanuję: {url}")
        crawl(url, url, max_pages_per_url)

    driver.quit()

# Uruchamiaj co 24 godziny
schedule.every(24).hours.do(main)

if __name__ == "__main__":
    print("🔄 Uruchomiono moduł pobierania danych...")
    main()
    while True:
        schedule.run_pending()
        time.sleep(1)

