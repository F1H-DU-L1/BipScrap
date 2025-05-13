import requests



#todo
#pobieranie z kolejki rabbita url

#todo
#wysyłanie dalej przez kolejke rabbita id diffa


def split_by_dot(text):
    return [part.strip() + '.' for part in text.split('.') if part.strip()]

def compare_documents(latest_doc, second_latest_doc):
    if not second_latest_doc:
        return latest_doc.strip()

    latest_sentences = split_by_dot(latest_doc)
    second_latest_set = set(split_by_dot(second_latest_doc))

    new_sentences = [s for s in latest_sentences if s not in second_latest_set]

    return ' '.join(new_sentences)



def fetch_documents(url, doc_id_key_1, doc_id_key_2):
    payload = {"URL": url}
    response = requests.post("http://localhost:5000/getdocs", json=payload)

    if response.status_code == 200:
        docs = response.json()
        latest_doc = docs.get("Latest doc")
        second_latest_doc = docs.get("Second latest doc")

        if latest_doc and second_latest_doc:
            diff_result = compare_documents(latest_doc, second_latest_doc)
            if diff_result:

                diff_payload = {
                    "doc_id_key_1": doc_id_key_1,
                    "doc_id_key_2": doc_id_key_2,
                    "content": diff_result
                }
                diff_response = requests.post("http://localhost:5000/diff", json=diff_payload)
                print("Wysłano różnice:", diff_response.json())

            else:
                print("Brak nowych zdań.")
        elif latest_doc:
            diff_payload = {
                "doc_id_key_1": doc_id_key_1,
                "doc_id_key_2": doc_id_key_2,
                "content": latest_doc
            }
            diff_response = requests.post("http://localhost:5000/diff", json=diff_payload)
            print("Wysłano różnice:", diff_response.json())
        else:
            print("Brakuje dokumentów.")
    else:
        print(f"Błąd pobierania dokumentów: {response.status_code}")
        print("Response:", response.text)





#przykładowe dane przed dodaniem rabbita
url_test = "https://bip.erzeszow.pl/100-urzad-miasta/4240-dobre-praktyki/87199-punkty-obslugi-mieszkancow.html"
id1_test=1
id2_test=6
fetch_documents(url_test, id1_test, id2_test)

