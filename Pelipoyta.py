from Pakka import Pakka
from Pelaaja import Pelaaja
from Jako import Jako

class Pelipoyta:
    def __init__(self, pelaajat: list):
        self.PerusPakka = Pakka()
        self.PerusPakka.luo_pakka()

        self.pelipakka = Pakka()
        self.pelipakka.kortit = self.PerusPakka.kortit.copy()
        
        self.pelaajat = pelaajat
        self.kierros = 0
        self.jakovuoro = 0
        self.ohi: bool = False
    

    def testiPeli(self):
        
        jakoja = 0
        while True:
            jakoja += 1
            for pelaaja in self.pelaajat:
                if pelaaja.chips <= 0:
                    pelaaja.aktiivinen = False
            self.uusiKierros()
            if self.ohi:
                print("Jakoja tähän hommaan tarvittiin", jakoja)
                break
            self.nollaaKierros()


    def uusiKierros(self): #TOI TULOS TÄYTYY MYÖHEMMIN KÄYDÄ LÄPI, JOTTA SE OSATAAN JAKAA TASAPELISSÄ ja miten sidepotit
        aktiiviset = []
        for pelaaja in self.pelaajat:
            if pelaaja.aktiivinen:
                aktiiviset.append(pelaaja)
        if len(aktiiviset) == 1: # TÄÄ VARMAAN KUULUU KIERROKSEN LOPPUUN, EI ALKUUN
            self.julistaVoittaja(aktiiviset[0])
            self.ohi = True
        else:
            jakaja = aktiiviset.index(self.paivitaJakaja())
            jako = Jako(self.pelipakka, aktiiviset, 100, jakaja)
            tulos = jako.pelaaKierros()
            print("TULOS: ", tulos)
            tulos[0][0]["pelaaja"].chips += tulos[1].summa
            
            for i in self.pelaajat:
                print(i.nimi, i.chips)

    def nollaaKierros(self): 
        for pelaaja in self.pelaajat:
            pelaaja.nollaaKierros()
            #if pelaajalla on chippejä niin aktiivinen on yksi, else ULOS
        self.pelipakka.kortit.clear()
        #discardpile, mihin tulee ja tarvitaanko miten?
        self.pelipakka.kortit = self.PerusPakka.kortit.copy()

    def julistaVoittaja(self, voittaja: Pelaaja):
        print("TÖTTÖTTÖRÖÖÖÖ RÖ TÖÖÖ!!!")
        print("MEILLÄ ON UUSI MESTARI!")
        print("HÄN KULKEE NIMELLÄ", voittaja.nimi, "JA PEITTOSI MUUT KERÄÄMÄLLÄ", voittaja.chips, "CHIPPIÄ!")
        print("ONNEA PONNEA!")

    def paivitaJakaja(self) -> Pelaaja: #Tän voisi kai kääntää ja kirjoittaa niin, että kun aktiviinen niin tapahtuu, muuten while true jatkuu
        while True:
            self.jakovuoro += 1
            if self.pelaajat[self.jakovuoro % len(self.pelaajat)].aktiivinen == False:
                continue
            else: # Toimiiko vai pitääkö laittaa jakaja = toi ja break ja return jakaja
                return self.pelaajat[self.jakovuoro % len(self.pelaajat)]


testipelaajat = [Pelaaja(nimi = "Ykkönen", tyyppi = "joku"), Pelaaja(nimi = "Kakkonen", tyyppi = "joku"), Pelaaja(nimi = "Kolmonen", tyyppi = "joku"), Pelaaja(nimi = "Nelonen", tyyppi = "joku")]
testipelaajat[1].aktiivinen = False
testipelaajat[0].aktiivinen = False
vuoro = 0

for i in range(10):
    while True:
        vuoro += 1
        print("Nyt on vuoro", vuoro)
        if testipelaajat[vuoro % len(testipelaajat)].aktiivinen == False:
            print("Pelaaja: ", testipelaajat[vuoro % len(testipelaajat)].nimi, "skipataan")
            continue
        else:
            #print("vuoro", vuoro, "ja laskun tulos ", vuoro % len(testipelaajat))
            jakaja = testipelaajat[vuoro % len(testipelaajat)]
            break
    print("Tämä palautetaan funktiosta:", jakaja)
    indeksi = testipelaajat.index(jakaja)
    print("indeksi", indeksi)
