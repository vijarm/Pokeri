from Pakka import Pakka
from Pelaaja import Pelaaja
from Jako import Jako
from random import randint

class Pelipoyta:
    def __init__(self, pelaajat: list):
        self.PerusPakka = Pakka()
        self.PerusPakka.luo_pakka()

        self.pelipakka = Pakka()
        self.pelipakka.kortit = self.PerusPakka.kortit.copy()
        
        self.pelaajat = pelaajat
        self.kierros: int = 0
        self.jakovuoro: int = randint(0, len(pelaajat) - 1)  #Ensimmäinen jakaja arvotaan
        self.ohi: bool = False
    

    def autoPeli(self):
        self.kierros = 0
        while True:
            self.kierros += 1
            for pelaaja in self.pelaajat:
                if pelaaja.chips <= 0:
                    pelaaja.aktiivinen = False
            self.uusiAutoKierros()
            if self.ohi:
                print("Jakoja tähän hommaan tarvittiin", self.kierros)
                break
            self.nollaaKierros()

    def testiPeli(self):
        self.kierros = 0
        while True:
            self.kierros += 1
            for pelaaja in self.pelaajat:
                if pelaaja.chips <= 0:
                    pelaaja.aktiivinen = False
            self.uusiKierros()
            if self.ohi:
                print("Jakoja tähän hommaan tarvittiin", self.kierros)
                break
            self.nollaaKierros()


    def uusiKierros(self): 
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
            #tulos[x] = tuplen indeksi, jos potteja on useita niin x > 1
            #tulos[x][0] = x:n voittopotin voittajapelaajat LISTA, tulos[x][1] = x:n voittopotin summa (int)
            #tulos[x][0][y] = x:n voittopotin voittajapelaajien y:s voittajapelaaja
            for x in range(len(tulos)):
                for y in range(len(tulos[x][0])):
                    tulos[x][0][y]["pelaaja"].chips += (tulos[x][1] // len(tulos[x][0]))
            
            for i in self.pelaajat:
                print(i.nimi, i.chips)

    def uusiAutoKierros(self): #Tätä muokataan yo. mukana TAI laitetaan muuttuja auto = 1, jonka perusteella pari asiaa muuttuu
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
            tulos = jako.autoKierros()
            print("TULOS: ", tulos)

            for x in range(len(tulos)):
                for y in range(len(tulos[x][0])):
                    tulos[x][0][y]["pelaaja"].chips += (tulos[x][1] // len(tulos[x][0]))
            
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

    def paivitaJakaja(self) -> Pelaaja: 
        while True:
            self.jakovuoro += 1
            if self.pelaajat[self.jakovuoro % len(self.pelaajat)].aktiivinen == False:
                continue
            else: 
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
