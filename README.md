Gotovo! Evo opisa za README datoteku na GitHubu za tvoju Python GUI MQTT aplikaciju. Jasno objašnjava svrhu, funkcionalnosti i kako se koristi.

---

# Python GUI MQTT Klijent za Pazin Automatizaciju

Ova aplikacija predstavlja intuitivan grafički korisnički interfejs (GUI) razvijen u Pythonu, namijenjen za nadzor temperature i kontrolu sustava ventilacije u prostorijama u Pazinu. Klijent komunicira s **Dasduino Connect (ESP8266)** prototipom putem **MQTT protokola**, omogućujući bežično upravljanje i praćenje u realnom vremenu.

---

## O projektu

Projekt je zamišljen kao centralizirano rješenje za interakciju s IoT uređajem koji mjeri temperaturu i upravlja ventilatorom. Povezivanjem na javni **HiveMQ broker**, aplikacija omogućuje fleksibilno upravljanje bez obzira na fizičku lokaciju.

---

## Značajke

* **Povezivanje s MQTT Brokerom:** Jednostavno spajanje i odspajanje s `broker.hivemq.com` na portu `1883`. Vizualna indikacija statusa veze.
* **Prikaz temperature u stvarnom vremenu:** Temperatura, koju Dasduino očitava s BMP180 senzora i objavljuje na `pazin/temperatura` topic, prikazuje se na istaknutom mjestu u sučelju.
* **Kontrola načina rada automatike:** Gumb za prebacivanje između ručnog i automatskog načina rada. Poruke (`ON`/`OFF`) se šalju na `pazin/automatika` topic.
* **Ručna kontrola ventilatora:** Gumb za uključivanje/isključivanje ventilatora slanjem poruka (`ON`/`OFF`) na `pazin/ventilator/kontrola` topic. Ova kontrola je aktivna samo kada je automatski način rada isključen (gumb je tada onemogućen).
* **Ažuriranje statusa:** Aplikacija vizualno prikazuje trenutni status automatike i ventilatora, te ažurira gumbe ovisno o stanju sustava.
* **Dnevnik događaja (Log):** Tekstualni prozor prikazuje sve relevantne MQTT poruke i statusne informacije za lakše praćenje.

---

## Tehnički detalji

* **Jezik:** Python 3
* **GUI Biblioteka:** `Tkinter` (ugrađena u Python)
* **MQTT Klijent:** `Paho-MQTT`
* **MQTT Broker:** `broker.hivemq.com` (javni testni broker)
* **Povezani hardver:** Dasduino Connect (ESP8266) s BMP180 senzorom i kontrolom digitalnog izlaza za ventilator.

---

## Instalacija

1.  **Klonirajte repozitorij:**
    ```bash
    git clone https://github.com/vase_korisnicko_ime/vas_repozitorij.git
    cd vas_repozitorij
    ```
2.  **Instalirajte potrebne Python pakete:**
    ```bash
    pip install paho-mqtt
    ```
    *(Napomena: `tkinter` dolazi ugrađen s većinom Python 3 instalacija.)*

---

## Korištenje

1.  **Pokrenite aplikaciju:**
    ```bash
    python naziv_vase_aplikacije.py # Zamijenite naziv_vase_aplikacije.py s pravim imenom datoteke
    ```
2.  **Spojite se na Broker:**
    Kliknite gumb **"Spoji / Odspoji"** za uspostavljanje veze s MQTT brokerom. Status veze bit će prikazan.
3.  **Pregled temperature:**
    Nakon spajanja, aplikacija će automatski početi prikazivati temperaturu koju šalje Dasduino (na `pazin/temperatura` topic).
4.  **Kontrola automatike:**
    Koristite gumb **"Uključi Automatiku" / "Isključi Automatiku"** za prebacivanje između načina rada. Status će se ažurirati.
5.  **Kontrola ventilatora:**
    Kada je automatika isključena, koristite gumb **"Uključi Ventilator" / "Isključi Ventilator"** za ručnu kontrolu. Kada je automatika uključena, gumb za ventilator bit će onemogućen.

---

**Napomena za developere:** Kod je struktuiran unutar klase za bolju organizaciju. MQTT komunikacija se odvija u pozadinskoj niti kako bi GUI ostao responzivan. Ponašanje pri zatvaranju aplikacije je prilagođeno za uredno odspajanje s brokera.
