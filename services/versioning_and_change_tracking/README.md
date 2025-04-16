# 📨 Text Diff Processor with RabbitMQ

Ten serwis w Pythonie nasłuchuje wiadomości z kolejki RabbitMQ, porównuje nowe teksty z poprzednimi wersjami i przesyła tylko **zmiany** (diffy) do innej kolejki.

## 📦 Funkcje

- 📥 Odbiera dane (URL + tekst) z wejściowej kolejki RabbitMQ.
- 🧠 Przechowuje ostatnią wersję tekstu (short_text) lokalnie (w `short_cache/`).
- 🧾 Porównuje nową wersję z poprzednią i generuje **tylko różnice** (dodane linie).
- 📤 Wysyła wynikowy diff jako JSON do wyjściowej kolejki.

---

## ⚙️ Wymagania

- Python 3.8+
- RabbitMQ
- Plik `.env` z konfiguracją

### 📁 .env przykład

```env
RABBITMQ_HOST=rabbitmq
RABBITMQ_USER=user
RABBITMQ_PASS=password
RABBITMQ_QUEUE=data_queue
RABBITMQ_OUTPUT_QUEUE=processed_queue
```


Wiadomość wejściowa (data_queue)
```
{
  "url": "http://example.com/page/1",
  "text": "Pełny tekst strony..."
}
```
Wiadomość wyjściowa (processed_queue)
```
{
  "url": "http://example.com/page/1",
  "diff": "Nowe dodane linie tekstu..."
}
```