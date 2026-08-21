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
        self.panos: int = 0

        self.pelivaihe = 0  # 1 = 1. panostus | 2 = vaihdot | 3 = 2. panostus | 4 = showdown
        self.jako = None
        self.tila = "peli"
        self.voittaja = None

        self.log = []
    

    def paivitaTila(self):

        if sum(p.aktiivinen for p in self.pelaajat) == 1:
            self.voittaja = next(p for p in self.pelaajat if p.aktiivinen)
            self.julistaVoittaja(self.voittaja)
            self.tila = "valmis"
            return

        if self.jako is None:
            self.uusiKierros()
            return

        self.jako.paivitaTila()

        if self.jako.tila != "valmis":
            return

        self.kasitteleJakoTulos()

        
    def autoPeli(self) -> Pelaaja:
        self.kierros = 0
        while True:
            self.kierros += 1
            self.uusiAutoKierros()
            self.lopetaKierros()

            if sum(p.aktiivinen for p in self.pelaajat) == 1:
                self.julistaVoittaja(next(p for p in self.pelaajat if p.aktiivinen))
                break
        print("Peli päättyi, jakoja voittajan löytämiseen tarvittiin", self.kierros)
        return next(p for p in self.pelaajat if p.aktiivinen)

    '''
    def testiPeli(self):
        self.paivitaNakymat()
        self.kierros = 0
        while True:  # TÄÄ MUUTTUU 
            self.kierros += 1
            self.uusiKierros()
            self.lopetaKierros()  #nollaa tiedot
                        
            if sum(p.aktiivinen for p in self.pelaajat) == 1:
                self.julistaVoittaja(next(p for p in self.pelaajat if p.aktiivinen))
                break
            self.paivitaNakymat()
        print("Peli päättyi, jakoja voittajan löytämiseen tarvittiin", self.kierros)
    '''
                     

    def uusiKierros(self): 
        aktiiviset = [p for p in self.pelaajat if p.aktiivinen and p.chips > 0]  #Vain aktiiviset pelaa, lisävarmistus chips > 0
        if len(aktiiviset) < 2: pass ##### TÄHÄN JOKU self.tila = valmis jos, peli on loppu. Pitäis kyllä tulla muualla.

        self.paivitaJakaja()
        self.paivitaPanos()
        self.kierros += 1

        self.jako = Jako(self)


    def kasitteleJakoTulos(self):
        assert self.jako is not None
        tulos = self.jako.tulos
        assert isinstance(tulos, list)
        #tulos[x] = tuplen indeksi, jos potteja on useita niin x > 1
        #tulos[x][0] = x:n voittopotin voittajapelaajat LISTA, tulos[x][1] = x:n voittopotin summa (int)
        #tulos[x][0][y] = x:n voittopotin voittajapelaajien y:s voittajapelaaja
        for x in range(len(tulos)):
            for y in range(len(tulos[x][0])):
                tulos[x][0][y]["pelaaja"].chips += (tulos[x][1] // len(tulos[x][0]))
                
        self.lopetaKierros()
        self.paivitaNakymat()
        self.jako = None


    def uusiAutoKierros(self): #Tätä muokataan yo. mukana TAI laitetaan muuttuja auto = 1, jonka perusteella pari asiaa muuttuu
        aktiiviset = [p for p in self.pelaajat if p.aktiivinen and p.chips > 0]  #Vain aktiiviset pelaa, lisävarmistus chips > 0
        if len(aktiiviset) < 2: return

        self.paivitaJakaja()
        self.paivitaPanos()

        self.jako = Jako(self)  
        #tulos = self.jako.pelaaKierros()  #Tää on se vanha looppi ja osa funktioista on muuttunut
        tulos = []

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

    def paivitaJakaja(self): 
        while True:
            self.jakovuoro += 1
            if self.pelaajat[self.jakovuoro % len(self.pelaajat)].aktiivinen == False:
                continue
            else: 
                self.jakaja = self.pelaajat[self.jakovuoro % len(self.pelaajat)]
                break

    def paivitaPanos(self):
        if self.kierros < 13:  #kierrokset 1-12, +50 joka 4. kierros
            self.panos = 100 + (50 * ((self.kierros - 1) // 4))
        elif (self.kierros - 1) % 4 == 0:
            if self.kierros > 28: #kierros > 29, +400 joka 4. kierros
                self.panos += 400
            elif self.kierros < 21: #kierroksilla 13 ja 17 +100
                self.panos += 100
            else:
                self.panos += 200 #väliin jäävillä 21 ja 25 +200


    def paivitaNakymat(self):  #Päivitetään näkymä, jota käytetään GUI:ssa ja jolla rajataan mitä kukakin näkee
        for pelaaja in self.pelaajat:
            pelaaja.nakyma = PelaajaNakyma(pelaaja, self)
            
            #TÄHÄN MYÖHEMMIN: Jos pelaaja = nettipelaaja client -> lähetä uusi näkymä

    def loggaa(self, teksti: str):
        self.log.append(teksti)

