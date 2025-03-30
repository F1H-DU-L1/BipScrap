import os
import csv
import hashlib
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Konfiguracja Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Tryb bez GUI
driver = webdriver.Chrome(options=chrome_options)

VISITED = set()
HEADERS = {"User-Agent": "Mozilla/5.0"}

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

def extract_main_content(soup, raw_html):
    """Usuwa nagłówek, stopkę, menu, head, paski nawigacyjne i inne zbędne elementy ze strony."""

    # Usuwamy niechciane tagi w BeautifulSoup
    for tag in soup.find_all(["header", "footer", "nav", "aside", "head", "script", "style"]):
        tag.decompose()

    # Czyszczenie treści strony
    cleaned_content = soup.get_text(strip=True)

    # Przetwarzamy surowy HTML
    raw_soup = BeautifulSoup(raw_html, "html.parser")

    # Usuwamy te same tagi z raw_soup
    for tag in raw_soup.find_all(["header", "footer", "nav", "aside", "head", "script", "style"]):
        tag.decompose()

    # Zwracamy oczyszczony HTML i treść
    cleaned_raw_html = str(raw_soup)
    return cleaned_content, cleaned_raw_html

def compute_file_hash(file_path):
    """Oblicza hash SHA-256 zawartości pliku (bez uwzględniania nazwy pliku)."""
    try:
        with open(file_path, "rb") as file:
            file_content = file.read()  # Odczytujemy zawartość pliku
            file_hash = hashlib.sha256(file_content).hexdigest()  # Obliczamy hash
        return file_hash
    except Exception as e:
        print(f"❌ Błąd przy obliczaniu hasha dla pliku {file_path}: {e}")
        return None

def create_hash_report(csv_file, html_file, output_txt_file):
    """Tworzy plik .txt z nazwami plików i ich hashami (csv i html)."""
    # Obliczamy hashe dla plików
    csv_hash = compute_file_hash(csv_file)
    html_hash = compute_file_hash(html_file)
    
    # Sprawdzamy, czy udało się obliczyć hashe
    if not csv_hash or not html_hash:
        print("❌ Nie udało się obliczyć hashy dla plików.")
        return
    
    # Tworzymy plik .txt z wynikami
    try:
        with open(output_txt_file, "w", encoding="utf-8") as output_file:
            output_file.write(f"Plik: {csv_file}\nHash: {csv_hash}\n\n")
            output_file.write(f"Plik: {html_file}\nHash: {html_hash}\n")
        print(f"✅ Zapisano raport hashy w pliku: {output_txt_file}")
    except Exception as e:
        print(f"❌ Błąd przy zapisywaniu raportu hashy: {e}")

def crawl(domain, base_url, max_pages_per_url = None):
    """Przeszukuje całą domenę i zbiera dane z podstron."""
    queue = [base_url]
    visited = set()
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    storage_dir = f"data/{urlparse(domain).netloc.replace('.', '_')}_{timestamp}/"
    os.makedirs(storage_dir, exist_ok=True)

    csv_file = os.path.join(storage_dir, f"scraped_{timestamp}.csv")
    html_file = os.path.join(storage_dir, f"scraped_{timestamp}.txt")
    sitemap_file = os.path.join(storage_dir, f"sitemap.txt")
    hash_file = os.path.join(storage_dir, f"hash_file.txt")

    with open(csv_file, "w", newline="", encoding="utf-8") as csv_out, \
         open(html_file, "w", encoding="utf-8") as html_out, \
         open(sitemap_file, "w", encoding="utf-8") as sitemap_out:

        writer = csv.writer(csv_out)
        writer.writerow(["URL", "Content"])

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
            content, html_content = extract_main_content(soup, raw_html)

            # Zapisywanie wyników
            writer.writerow([url, content])
            html_out.write(f"URL: {url}\n{html_content}\n\n")
            sitemap_out.write(url + "\n")
            print(f"📄 Zapisano stronę: {url}")

            # Szukanie kolejnych podstron
            links_to_visit = []
            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"])

                # Dodajemy tylko linki do tej samej domeny
                if urlparse(full_url).netloc == urlparse(base_url).netloc and full_url not in visited:
                    links_to_visit.append(full_url)

            # Debugging: Sprawdzamy, czy są linki do odwiedzenia
            if links_to_visit:
                print(f"🔗 Zebrane linki do odwiedzenia: {links_to_visit}")
            else:
                print(f"🔗 Brak linków do odwiedzenia na stronie {url}")

            # Przetwarzanie linków na stronie (kliknięcie w linki)
            for next_url in links_to_visit:
                if next_url not in visited:
                    print(f"🔗 Dodawanie podstrony: {next_url}")
                    queue.append(next_url)

            time.sleep(1)  # Unikanie przeciążenia serwera
            
    # Oblicza i zapisuje hashe zawartości plików
    create_hash_report(csv_file, html_file, hash_file)

def main():
    """Główna funkcja uruchamiająca skrypt."""
    urls = [
        "http://quotes.toscrape.com/",
        "http://quotes.toscrape.com/js"
    ]
    
    max_pages_per_url = 5  # Limit podstron, np. 15. Można ustawić na None, aby nie było limitu.

    for url in urls:
        print(f"🌍 Skanuję: {url}")
        crawl(url, url, max_pages_per_url)

    driver.quit()

if __name__ == "__main__":
    main()
