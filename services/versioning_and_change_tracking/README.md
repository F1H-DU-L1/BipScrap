# 📨 Text Diff Processor with RabbitMQ

Ten serwis w Pythonie nasłuchuje wiadomości z kolejki RabbitMQ, porównuje nowe teksty z poprzednimi wersjami i przesyła **zmiany** (diffy) do bazy danych oraz wiadomość do kolejki.

## 📦 Funkcje

- 📥 Odbiera dane (URL) z wejściowej kolejki RabbitMQ.
- 🧾 Porównuje nową wersję z poprzednią i generuje **tylko różnice**.
- 📤 Wysyła wynikowy diff do bazy oraz wiadomość do kolejki.

---

## ⚙️ Wymagania

- Python 3.8+
- RabbitMQ
- Plik `.env` z konfiguracją

### 📁 .env przykład

```env
RABBITMQ_HOST=rabbitmq
RABBITMQ_USER=admin
RABBITMQ_PASS=admin
RABBITMQ_INPUT_QUEUE=t1t2
RABBITMQ_OUTPUT_QUEUE=t2t3
DATA_MANAGEMENT_HOST=data_management
DATA_MANAGEMENT_PORT=5000
```


Wiadomość wejściowa (data_queue)
```
{
  "url": "http://example.com/page/1",
}
```
Wiadomość wyjściowa (processed_queue)
```
{
  "doc_diff_id": "2",
}
```