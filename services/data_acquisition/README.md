# Skrypt Web Scraping

Ten skrypt służy do web scrapingu z użyciem Selenium oraz BeautifulSoup. Skrypt przeszukuje strony internetowe, zbiera treść z różnych podstron, a następnie zapisuje dane do plików CSV, HTML oraz tworzy plik TXT z adresami przetworzonych podstron. Dodatkowo, skrypt oblicza hash SHA-256 dla wygenerowanych plików i tworzy raport.

## .env
RABBITMQ_USER: ""
RABBITMQ_PASS: ""
RABBITMQ_HOST: ""
RABBITMQ_QUEUE: ""

## Instalacja

Upewnij się, że masz zainstalowany Python w wersji 3.6 lub wyższej. Następnie uruchom poniższe polecenie, aby zainstalować zależności:

```bash
pip install -r requirements.txt
```

Skrypt wymaga następujących pakietów:

- `selenium`
- `beautifulsoup4`
- `requests`
- `hashlib`
- `time`
- `os`
- `csv`
<<<<<<< HEAD

## Opis funkcji

### 1. `get_soup_selenium(url)`
=======
- `json`
- `pika`
- `dotenv`
- `schedule`

## Opis funkcji

### 1. `send_to_rabbitmq(url, text)`
**Opis** Funkcja przesyła do kolejki rabbitMQ adresy URL i zawartość stron

### 2. `get_soup_selenium(url)`
>>>>>>> 5f2f32b (Dodanie kolejki rabbitmq do modułu zbierania danych.)
**Opis**: Funkcja pobiera stronę internetową za pomocą Selenium, czekając na załadowanie wszystkich elementów strony, w tym tych dynamicznych ładowanych przez JavaScript. Zwraca obiekt `BeautifulSoup` oraz surowy HTML.

**Wejście**:
- `url`: Adres URL strony do pobrania.

**Wyjście**:
- `soup`: Obiekt `BeautifulSoup` z zawartością strony.
- `raw_html`: Surowy HTML strony.

<<<<<<< HEAD
### 2. `extract_main_content(soup, raw_html)`
=======
### 3. `extract_main_content(soup, raw_html)`
>>>>>>> 5f2f32b (Dodanie kolejki rabbitmq do modułu zbierania danych.)
**Opis**: Funkcja usuwa nagłówki, stopki, paski nawigacyjne, skrypty oraz inne zbędne elementy ze strony i jej surowego HTML-a. Zwraca oczyszczoną treść strony oraz oczyszczony HTML.

**Wejście**:
- `soup`: Obiekt `BeautifulSoup` zawierający stronę HTML.
- `raw_html`: Surowy HTML strony.

**Wyjście**:
- `content`: Oczyszczona treść strony.
- `cleaned_raw_html`: Oczyszczony HTML strony.

<<<<<<< HEAD
### 3. `compute_file_hash(file_path)`
=======
### 4. `compute_file_hash(file_path)`
>>>>>>> 5f2f32b (Dodanie kolejki rabbitmq do modułu zbierania danych.)
**Opis**: Funkcja oblicza hash SHA-256 dla pliku wskazanego przez ścieżkę.

**Wejście**:
- `file_path`: Ścieżka do pliku, którego hash ma zostać obliczony.

**Wyjście**:
- `file_hash`: Hash SHA-256 pliku.

<<<<<<< HEAD
### 4. `create_hash_report(csv_file, html_file, output_txt_file)`
=======
### 5. `create_hash_report(csv_file, html_file, output_txt_file)`
>>>>>>> 5f2f32b (Dodanie kolejki rabbitmq do modułu zbierania danych.)
**Opis**: Funkcja generuje raport w formacie tekstowym zawierający hashe plików CSV oraz HTML.

**Wejście**:
- `csv_file`: Ścieżka do pliku CSV.
- `html_file`: Ścieżka do pliku HTML.
- `output_txt_file`: Ścieżka do pliku, w którym zapisany zostanie raport hashy.

**Wyjście**:
- Zapisuje raport hashy do pliku tekstowego.

<<<<<<< HEAD
### 5. `crawl(domain, base_url, max_pages_per_url=None)`
=======
### 6. `crawl(domain, base_url, max_pages_per_url=None)`
>>>>>>> 5f2f32b (Dodanie kolejki rabbitmq do modułu zbierania danych.)
**Opis**: Funkcja do przeszukiwania domeny i zbierania danych z podstron. Funkcja pobiera strony, oczyszcza treść, zapisuje dane do plików CSV, HTML oraz mapy witryny. Działa rekurencyjnie, przetwarzając wszystkie dostępne podstrony.

**Wejście**:
- `domain`: Domena strony, która ma zostać przeszukana.
- `base_url`: Podstawowy URL, od którego rozpoczyna się skanowanie.
- `max_pages_per_url` (opcjonalnie): Limit liczby podstron do przetworzenia dla każdej domeny. Domyślnie brak limitu (None).

**Wyjście**:
- Zapisuje dane w plikach:
  - `scraped_<timestamp>.csv`: Zawiera URL i oczyszczoną treść każdej strony.
  - `scraped_<timestamp>.txt`: Zawiera surowy HTML każdej strony.
  - `sitemap.txt`: Zawiera listę przetworzonych URL.
  - `hash_file.txt`: Zawiera raport hashy dla plików CSV i HTML.

<<<<<<< HEAD
### 6. `main()`
=======
### 7. `main()`
>>>>>>> 5f2f32b (Dodanie kolejki rabbitmq do modułu zbierania danych.)
**Opis**: Funkcja główna uruchamiająca skrypt. Uruchamia przetwarzanie dla listy podanych URL-i.

**Wejście**:
- `urls`: Lista URL-i do przetworzenia.
- `max_pages_per_url`: Limit liczby podstron do przetworzenia.

**Wyjście**:
- Uruchamia proces crawlowania i zapisuje dane do odpowiednich plików.

## Przykład użycia

### Skrypt

W pliku `main.py` można ustawić listę URL-i, które mają być przetworzone, oraz limit podstron.

```python
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
```

### Uruchomienie skryptu

Aby uruchomić skrypt, po prostu uruchom plik Python:

```bash
python webscrapping.py
```

Skrypt przetworzy podane URL-e i zapisze wyniki do plików w folderze `data/`, tworząc podfoldery w zależności od daty i godziny uruchomienia.

## Pliki wyjściowe

Po zakończeniu przetwarzania skrypt tworzy następujące pliki:

- **CSV**: `scraped_<timestamp>.csv`
  - Zawiera kolumny: URL, Content (oczytana treść strony).
  
- **HTML**: `scraped_<timestamp>.txt`
  - Zawiera pełny surowy HTML stron.
  
- **Mapa witryny**: `sitemap.txt`
  - Zawiera listę URL-i przetworzonych podczas skanowania.
  
- **Raport hashy**: `hash_file.txt`
  - Zawiera SHA-256 hashe dla plików CSV i HTML.

## Ustawienia

### `urls`:
- Lista URL-i, które mają zostać przetworzone.

### `max_pages_per_url`:
- Ogranicza liczbę podstron do przetworzenia z danej domeny. Można ustawić na `None`, aby nie było limitu.

### Przykład raportu hashy w `hash_file.txt`:

```
Plik: data/quotes_toscrape_com_20250330/scraped_20250330.csv
Hash: d2d2d2a55c4a52e4eb2e28a7cd582c6a15d1b9da59302a512ef47ba1f34a4045

Plik: data/quotes_toscrape_com_20250330/scraped_20250330.txt
Hash: f1c1e0aaf343a82f8a87cc8c1ac6d85fc7393a274890d8f9837172dbba3d45d0
```

## Licencja

Ten skrypt jest udostępniany na licencji MIT.
