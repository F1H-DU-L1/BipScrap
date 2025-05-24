# Lekki obraz Pythona
FROM python:3.11-slim

# Instalacja przydatnych narzędzi (opcjonalnie, ale spójne z innymi modułami)
RUN apt update && apt install -y wget curl unzip jq netcat-openbsd

# Skopiowanie skryptu wait-for-it.sh do kontenera
COPY ../../wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Ustawiamy katalog roboczy
WORKDIR /app

# Kopiujemy plik requirements (utworzymy go zaraz poniżej)
COPY services/versioning_and_change_tracking/requirements.txt .

# Instalujemy zależności
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy skrypt aplikacji
COPY services/versioning_and_change_tracking/versioning.py .

# Zmienne środowiskowe domyślne (mogą być nadpisane przez `.env`)


# Uruchomienie aplikacji po sprawdzeniu, że RabbitMQ działa
CMD ["wait-for-it.sh", "rabbitmq:5672", "-t", "30", "--", "python", "versioning.py"]
