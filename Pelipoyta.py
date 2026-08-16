from Pakka import Pakka
from Pelaaja import Pelaaja, PelaajaNakyma
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
        self.jakaja: Pelaaja = self.pelaajat[self.jakovuoro % len(self.pelaajat)]

        self.pelivaihe = 0  # 1 = 1. panostus | 2 = vaihdot | 3 = 2. panostus | 4 = showdown
        self.jako = None
    

    def autoPeli(self):
        self.kierros = 0
        while True:
            self.kierros += 1
            self.uusiAutoKierros()
            self.lopetaKierros()

            if sum(p.aktiivinen for p in self.pelaajat) == 1:
                self.julistaVoittaja(next(p for p in self.pelaajat if p.aktiivinen))
                break
        print("Peli päättyi, jakoja voittajan löytämiseen tarvittiin", self.kierros)


    def testiPeli(self):
        self.kierros = 0
        while True:
            self.kierros += 1
            self.uusiKierros()
            self.lopetaKierros()  #nollaa tiedot
                        
            if sum(p.aktiivinen for p in self.pelaajat) == 1:
                self.julistaVoittaja(next(p for p in self.pelaajat if p.aktiivinen))
                break
            self.paivitaNakymat()
        print("Peli päättyi, jakoja voittajan löytämiseen tarvittiin", self.kierros)
                     

    def uusiKierros(self):  #onko merkitystä hakeeko tämä sisällä aktiiviset, vai syötetäänkö siihen parametrina...
        aktiiviset = [p for p in self.pelaajat if p.aktiivinen and p.chips > 0]  #Vain aktiiviset pelaa, lisävarmistus chips > 0
        if len(aktiiviset) < 2: return

        jakaja = aktiiviset.index(self.paivitaJakaja())
        panos = 100 + (50 * ((self.kierros - 1) // 4))  #panos nousee 50% alkupanoksesta joka 4. kierros, voi myös muuttaa muuttujaksi

        self.jako = Jako(self)  
        # def __init__(self, pelipakka, pelaajalista: list, alkupanos: int, jakaja: int):
        tulos = self.jako.pelaaKierros()

        print("TULOS: ", tulos)
        #tulos[x] = tuplen indeksi, jos potteja on useita niin x > 1
        #tulos[x][0] = x:n voittopotin voittajapelaajat LISTA, tulos[x][1] = x:n voittopotin summa (int)
        #tulos[x][0][y] = x:n voittopotin voittajapelaajien y:s voittajapelaaja
        for x in range(len(tulos)):
            for y in range(len(tulos[x][0])):
                tulos[x][0][y]["pelaaja"].chips += (tulos[x][1] // len(tulos[x][0]))
                self.paivitaNakymat() #Joku pottikohtainen näytä ja click to continue tai sleep

        for i in self.pelaajat:
            print(i.nimi, i.chips)

    def uusiAutoKierros(self): #Tätä muokataan yo. mukana TAI laitetaan muuttuja auto = 1, jonka perusteella pari asiaa muuttuu
        aktiiviset = [p for p in self.pelaajat if p.aktiivinen and p.chips > 0]  #Vain aktiiviset pelaa, lisävarmistus chips > 0
        if len(aktiiviset) < 2: return

        jakaja = aktiiviset.index(self.paivitaJakaja())
        panos = 100 + (50 * ((self.kierros - 1) // 4))  #panos nousee 50% alkupanoksesta joka 4. kierros, voi myös muuttaa muuttujaksi

        self.jako = Jako(self)  
        tulos = self.jako.autoKierros()

        print("TULOS: ", tulos)

        for x in range(len(tulos)):
            for y in range(len(tulos[x][0])):
                tulos[x][0][y]["pelaaja"].chips += (tulos[x][1] // len(tulos[x][0]))
        
        for i in self.pelaajat:
            print(i.nimi, i.chips)

    def lopetaKierros(self): 
        for pelaaja in self.pelaajat:
            pelaaja.nollaaKierros()
            if pelaaja.chips <= 0:
                pelaaja.aktiivinen = False
        self.pelipakka.kortit.clear()
        #discardpile, mihin tulee ja tarvitaanko miten?
        self.pelipakka.kortit = self.PerusPakka.kortit.copy()

    def julistaVoittaja(self, voittaja: Pelaaja):
        self.paivitaNakymat()
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
                self.jakaja = self.pelaajat[self.jakovuoro % len(self.pelaajat)]
                return self.jakaja


    def paivitaNakymat(self):  #Päivitetään näkymä, jota käytetään GUI:ssa ja jolla rajataan mitä kukakin näkee
        for pelaaja in self.pelaajat:
            pelaaja.nakyma = PelaajaNakyma(pelaaja, self)
            
            #TÄHÄN MYÖHEMMIN: Jos pelaaja = nettipelaaja client -> lähetä uusi näkymä

