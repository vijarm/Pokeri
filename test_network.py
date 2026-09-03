import time

from transport import NetworkTransport
from viestit import Komento, Paivitys
from Pelaaja import PelaajaNakyma
from Pakka import Kortti


PORT = 5000


# --------------------------------------------------
# HOST
# --------------------------------------------------

host = NetworkTransport(
    mode="host",
    host="0.0.0.0",
    port=PORT
)


# --------------------------------------------------
# CLIENT
# --------------------------------------------------

client = NetworkTransport(
    mode="client",
    host="127.0.0.1",
    port=PORT
)


print("\n--- Yhteys muodostettu ---")


# --------------------------------------------------
# CLIENT LÄHETTÄÄ KOMENNON
# --------------------------------------------------

komento = Komento(
    "ok",
    "Testipelaaja"
)

print("CLIENT lähettää:", komento.tapahtuma, komento.pelaaja)

client.send_to_engine(komento)


# --------------------------------------------------
# ANNETAAN TCP:LLE HETKI AIKAA
# --------------------------------------------------

time.sleep(0.1)


# --------------------------------------------------
# HOST VASTAANOTTAA
# --------------------------------------------------

komennot = host.receive_for_engine()

print("\nHOST vastaanotti:")

for socket, komento in komennot:
    print(
        "  tyyppi:",
        type(komento).__name__,
        "| tapahtuma:",
        komento.tapahtuma,
        "| pelaaja:",
        komento.pelaaja
    )


# --------------------------------------------------
# TARKISTUKSET
# --------------------------------------------------

assert len(komennot) == 1

komento = komennot[0][1]

assert isinstance(komento, Komento)
assert komento.tapahtuma == "ok"
assert komento.pelaaja == "Testipelaaja"

print("\nTESTI ONNISTUI!")


# ----------------- TOINEN TESTI -------------------

# Samat host ja client


# --------------------------------------------------
# Tehdään testinäkymä käsin
# --------------------------------------------------

nakyma = PelaajaNakyma.__new__(PelaajaNakyma)

nakyma.nimi = "Testipelaaja"
nakyma.aktiivinen = True
nakyma.chips = 100
nakyma.allin = False
nakyma.maksettuJakoon = 10
nakyma.maksettuPanostukseen = 5
nakyma.valinta = 1
nakyma.vaihtoja = 2
nakyma.kasikortit = [Kortti(["HERTTA"], 5), Kortti(["RISTI"], 11), Kortti(["PATA"], 2), Kortti(["HERTTA"], 5), Kortti(["RUUTU"], 5)]

nakyma.pelivaihe = 1
nakyma.kierros = 3
nakyma.jakaja = "Jakaja"
nakyma.log = ["Testilogi"]

nakyma.potti = 50
nakyma.mukanaPotissa = ["Testipelaaja"]
nakyma.panos = 10

nakyma.pelaajaVuorossa = "Testipelaaja"
nakyma.suurinKorotus = 20
nakyma.maksettavaa = 15
nakyma.pieniKorotus = 10
nakyma.suuriKorotus = 30
nakyma.folded = False

nakyma.muutPelaajat = []


# --------------------------------------------------
# HOST → CLIENT
# --------------------------------------------------

paivitys = Paivitys(
    "pelipoyta",
    {"tapahtuma": "testi"},
    nakyma
)

print("HOST lähettää Paivityksen")

host.send_to_all_gui(paivitys)

time.sleep(0.2)


# --------------------------------------------------
# CLIENT vastaanottaa
# --------------------------------------------------

paivitykset = client.receive_for_gui()

print("\nCLIENT vastaanotti:")

for p in paivitykset:
    print("  tyyppi:", p.tyyppi)
    print("  tiedot:", p.tiedot)
    print("  näkymä:", p.uusinakyma.nimi)
    print("  chips:", p.uusinakyma.chips)


# --------------------------------------------------
# TARKISTUS
# --------------------------------------------------

vastaanotettu = paivitykset[0]

assert isinstance(vastaanotettu, Paivitys)
assert isinstance(vastaanotettu.uusinakyma, PelaajaNakyma)

assert vastaanotettu.tyyppi == paivitys.tyyppi
assert vastaanotettu.tiedot == paivitys.tiedot
assert vastaanotettu.uusinakyma.nimi == nakyma.nimi
assert vastaanotettu.uusinakyma.to_dict() == nakyma.to_dict()

print("\nKOKO PelaajaNakyma-DATA ON SAMA!")
print("\nHOST → CLIENT TESTI ONNISTUI!")