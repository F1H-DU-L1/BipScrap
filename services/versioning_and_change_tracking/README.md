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
RABBITMQ_USER=rabbit
RABBITMQ_PASS=rabbit
RABBITMQ_QUEUE=t1t2
RABBITMQ_OUTPUT_QUEUE=t2t3
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