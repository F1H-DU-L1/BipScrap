# Skrypt do Web Scraping

Ten skrypt jest zaprojektowany do przeszukiwania stron internetowych, pobierania zawartości z określonych URL-i, oraz przetwarzania plików PDF i DOCX. Zawartość jest następnie wysyłana do kolejki RabbitMQ i zapisywana w pliku CSV. Cały proces może być zaplanowany do uruchamiania automatycznie co 24 godziny.

## Wymagania

Przed uruchomieniem skryptu upewnij się, że masz zainstalowane następujące zależności:

1. **Zainstaluj zależności z pliku `requirements.txt`**:
   - Stwórz wirtualne środowisko (opcjonalnie, ale zalecane):
     ```bash
     python -m venv venv
     source venv/bin/activate  # Na systemach Linux lub macOS
     venv\Scripts\Activate.ps1     # Na Windows
     ```

   - Zainstaluj wymagane biblioteki:
     ```bash
     pip install -r requirements.txt
     ```

## Konfiguracja

### 1. Konfiguracja WebDrivera Selenium
   - **Pobierz odpowiednią wersję ChromeDriver**:
     - Upewnij się, że masz odpowiednią wersję ChromeDrivera, która pasuje do wersji Twojej przeglądarki Chrome. Pobierz go ze strony [ChromeDriver download](https://sites.google.com/chromium.org/driver/).
     - Zaktualizuj ścieżkę do ChromeDrivera w skrypcie:
       ```python
       service = Service("/ścieżka/do/chromedrivera")
       ```
     - Upewnij się, że `chromedriver` jest dostępny globalnie lub podaj pełną ścieżkę w skrypcie.

### 2. Konfiguracja katalogu pobierania (.env)
   - Zmień katalog pobierania w skrypcie na odpowiednią ścieżkę na Twoim systemie:
     ```python
     download_dir = "ścieżka/do/katalogu/pobierania"
     ```
   - Jest to miejsce, w którym zostaną zapisane pobrane pliki (PDF, DOCX) przed ich przetworzeniem.
   - Ścieżka musi być absolutna, relatwyna nie będzie działać.

### 3. Konfiguracja RabbitMQ
   - Ustaw serwer RabbitMQ i skonfiguruj dane połączenia:
     - Stwórz plik `.env` w głównym katalogu projektu i dodaj następujące zmienne:
       ```env
       RABBITMQ_HOST=adres_twojego_rabbitmq
       RABBITMQ_QUEUE=nazwa_twojej_kolejki
       RABBITMQ_USER=użytkownik_rabbitmq
       RABBITMQ_PASS=hasło_rabbitmq
       ```

### 4. Konfiguracja zmiennych środowiskowych
   - Zmienne dotyczą folderu pobierania, RabbitMQ oraz danych dostępu do abzy danych:
   | Variable Name      | Description                                   | Example                     |
   |--------------------|-----------------------------------------------|-----------------------------|
   | `DIRECTORY_DIR`     | Absolute directory path for downloads or file storage | `/home/user/downloads`       |
   | `RABBITMQ_HOST`     | Hostname or IP address of RabbitMQ server     | `rabbitmq.local`             |
   | `RABBITMQ_QUEUE`    | Name of the RabbitMQ queue to consume from    | `task_queue`                 |
   | `RABBITMQ_USER`     | Username for RabbitMQ authentication           | `guest`                     |
   | `RABBITMQ_PASS`     | Password for RabbitMQ authentication           | `guest`                     |
   | `DATABASE_URL`      | Full connection string for PostgreSQL          | `postgresql://user:pass@host:5432/dbname` |
   | `MAX_PAGES`         | Max scannable subpages                         | `postgresql://user:pass@host:5432/dbname` |

## Działanie skryptu

### Opis funkcji

#### 1. `extract_text_from_file(file_url)`
   **Wejście**: URL pliku (PDF lub DOCX), który ma zostać pobrany i przetworzony.  
   **Działanie**: Pobiera plik, czeka aż zostanie pobrany, a następnie wyciąga z niego tekst. Obsługiwane formaty to PDF i DOCX.  
   **Wyjście**: Zawartość tekstowa pliku lub `None` w przypadku błędu.

#### 2. `send_to_rabbitmq(scrap_id, url)`
   **Wejście**: `scrap_id` (unikalny identyfikator zbierania danych) i `url` (adres URL do wysłania).  
   **Działanie**: Łączy się z RabbitMQ, wysyła dane do określonej kolejki.  
   **Wyjście**: Brak. Funkcja nie zwraca wartości, ale wysyła dane do kolejki RabbitMQ.

#### 3. `get_soup_selenium(url)`
   **Wejście**: `url` strony, którą chcemy pobrać.  
   **Działanie**: Używa Selenium do załadowania strony, czekając na jej pełne załadowanie.  
   **Wyjście**: Zwraca obiekt BeautifulSoup z przetworzonym HTML oraz surowy kod HTML.

#### 4. `extract_main_content(soup)`
   **Wejście**: Obiekt BeautifulSoup, który zawiera całą stronę HTML.  
   **Działanie**: Usuwa zbędne elementy strony takie jak nagłówki, stopki, paski nawigacyjne i inne.  
   **Wyjście**: Zwraca oczyszczoną zawartość strony w postaci tekstu.

#### 5. `crawl(domain, base_url, max_pages_per_url)`
   **Wejście**: `domain` (główna domena do przeszukiwania), `base_url` (pierwsza strona do skanowania), `max_pages_per_url` (opcjonalny limit stron do przetworzenia).  
   **Działanie**: Rekurencyjnie przeszukuje strony w obrębie danej domeny, zbiera dane i zapisuje je w bazie danych. Przetwarza pliki PDF i DOCX.  
   **Wyjście**: Brak (dane są zapisywane w bazie danych i wysyłane do RabbitMQ).

## Ogólny opis działania skryptu

Skrypt rozpoczyna działanie od zdefiniowania listy URL-i w funkcji `main()`. Następnie przetwarza te strony, wyciągając z nich tekst. Dodatkowo, gdy znajdzie linki do plików PDF lub DOCX (DOC są pomijane), próbuje je pobrać i przetworzyć. Dane są wysyłane do kolejki RabbitMQ i zapisywane w bazie danych.

### Możliwość ustawienia limitu podstron
Skrypt umożliwia ustawienie limitu przetworzonych podstron na każdej stronie (w zmiennej `max_pages_per_url`). Jeśli limit zostanie osiągnięty, skrypt zaprzestanie dalszego przetwarzania tego URL-a.

### Harmonogram (Schedule)
Skrypt jest zaplanowany do uruchamiania co 24 godziny za pomocą biblioteki `schedule`. Możesz łatwo zmienić częstotliwość uruchamiania, modyfikując odpowiednią linijkę w kodzie:
```python
schedule.every(24).hours.do(main)
```
