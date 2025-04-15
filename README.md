# BipScrap
Przedmiotem projektu jest implementacja systemu do akwizycji i analizy danych. Głównym celem będzie webscrapping treści z serwisów typu Biuletynu Informacji Publicznej gmin. Treści powinny być zapisane w repozytorium aby zapewnić ich dalszą analizę. System powinien zapewniać możliwość identyfikowania zmian treści, tak aby analizie podlegała tylko zmieniona treść. Analiza będzie polegała na użyciu rozwiązań opartych o LLM do generowania notatek podsumowujących zidentyfikowane zmiany.
Systemu powinien być podzielony na odpowiednie moduły, zapewniające możliwość skalowania. Moduły powinny być zorganizowane w formie mikro-serwisów. Każdy moduł to oddzielny kontener z niezbędnymi interfejsami udostępnionymi na zewnątrz.
Każdy z modułów powinien posiadać jasno zdefiniowane interfejsy, które umożliwią komunikację z innymi modułami.
Należy zaproponować repozytorium, które będzie właściwe do przechowywania danych jak opisano w opisie projektu.
System powinien być oparty na języku Python.

Zespół 1.
Moduł akwizycji danych: odpowiedzialny za webscrapping treści z różnych źródeł i przekazanie do repozytorium.
· Wejście: URL źródła, harmonogram zbierania danych
· Wyjście: surowe dane HTML/tekstowe zapisane w repozytorium
Należy pobrać dane tak aby przejść przez wszystkie dokumenty (podstrony, pdfy, docx,…) do których są linki ze strony głównej.

Zespół 2. 
Moduł wersjonowania i śledzenia zmian: przechowuje pobraną treść, identyfikuje zmiany w źródle i przekazuje do dalszej analizy tylko zmienione fragmenty.
· Wejście: dane z Modułu akwizycji
· Wyjście: różnice w treści oraz aktualne wersje zapisane w repozytorium
Zapewnia przekazanie do analizy takiego zakresu zidentyfikowanych zmian, które pozwolą przeprowadzić analizę za pomocą LLM.

Zespół 3. Piotr Grabias, Kacper Dulemba, Paweł Dendura
Moduł podsumowujący zmiany treści: wykorzystuje modele LLM do generowania podsumowań dla znalezionych treści.
· Wejście: nowe lub zmienione treści
· Wyjście: notatki podsumowujące zmiany
Można użyć OpenAI lub lokalne modele jak LLama2. Preferowane są obydwa rozwiązania z możliwością przełączania implementacji na interfejsie.

Zespół 4.
Moduł zarządzania metadanymi i indeksowania: utrzymuje indeks treści i ich wersji oraz zapewnia łatwe wyszukiwanie danych w repozytorium.
· Wejście: wszystkie wersje i analizy
· Wyjście: strukturalny indeks danych, umożliwiający szybkie wyszukiwanie i filtrację
Dokumenty i diffy powinny być zapisane w postaci embeddingów lub innych wektorów, które można łatwo przeszukiwać. (np. Elasticsearch, MongoDB, PostgreSQL z pełnotekstowym wyszukiwaniem).

Zespół 6. (2 osoby)

Koordynacja i DevOps
· Dodać projekt do github, uruchomić CI/CD pipeline.
· Przygotowanie środowiska kontenerowego (Docker Compose, Kubernetes manifests).
· Środowisko testowe i stagingowe: prowadzenie testów integracyjnych i środowisk testowych.

Standard dokumentacji:
· opis modułów (README dla każdego mikro-serwisu).
· instrukcje wdrożeniowe.

Repozytorium surowych danych
Dla każdej unikalnej strony (każdego URL) należy przewidzieć oddzielny rekord w bazie danych. Taki rekord może zawierać następujące pola:
· URL: unikalny identyfikator dla danej strony.
· Treść strony: pobrana zawartość (może być w formie HTML, tekstu, JSON lub innego wybranego formatu).
· Metadane: informacje pomocnicze, takie jak data i czas pobrania, tytuł strony, ewentualny kod odpowiedzi HTTP, rozmiar treści, typ danych (HTML, PDF, itp.)
· Wersja: numer lub znacznik wersji pozwalający śledzić zmiany treści.
· Źródło i kategoria: oznaczenie, do jakiej gminy/serwisu/tematyki należy dana treść.
Kolejne wersje dla danego URL można zapisać jako różnice (diffy) w dedykowanym polu, aby efektywnie porównywać i aktualizować dane. W pierwszej iteracji można też rozważyć zapisywanie całości w kolejnym rekordzie z odpowiednią informacją o czasie/wersji, która pozwoli na analizę różnic.

## .env
RABBITMQ_DEFAULT_USER: ""
RABBITMQ_DEFAULT_PASS: ""