from Pistelasku import laskeArvot, haeVoittaja
from Pelaaja import Pelaaja
from Panostus import PanostusKierros
from random import randint


class Jako:
    def __init__(self, pelipoyta):
        self.pelipoyta = pelipoyta
        self.pakka = pelipoyta.pelipakka
        self.pelaajat = [p for p in pelipoyta.pelaajat if p.aktiivinen and p.chips > 0]
        self.mukanaPotissa = self.pelaajat.copy()
        self.potti = 0
        self.alkupanos = 100 + (50 * ((pelipoyta.kierros - 1) // 4))  #panos nousee 50% alkupanoksesta joka 4. kierros, voi myös muuttaa muuttujaksi
        self.jakaja = self.pelaajat.index(pelipoyta.paivitaJakaja()) #Jakajan indeksi pelaajalistasta
        self.panostuskierros = None

        self.pakka.sekoita()

    def pelaaKierros(self) -> list:
        self.keraaAlkupanokset()       
        self.pelipoyta.paivitaNakymat()  #Myös tässä välissä jos tulee joku all-in trigger tms?     
        self.jaaKortit()
        self.pelipoyta.paivitaNakymat()

        #panostuskierros ennen vaihtoja
        self.pelipoyta.pelivaihe = 1
        self.panostuskierros = PanostusKierros(self, self.pelipoyta)
        voittaja = self.panostuskierros.suoritaKierros()
        self.pelipoyta.paivitaNakymat()
        if voittaja:
            print("KAIKKI MUUT FOLDASI JA", voittaja.nimi, "voitti!")
            return [(haeVoittaja([voittaja]), self.potti)]  #Kierrätetään haeVoittaja -kautta, eli käsi evaluoidaan ja näytetään aina? Pitää palauttaa listana!

        #vaihdot, alkaa jakajasta seuraavasta:
        self.pelipoyta.pelivaihe = 2
        for i in range(1, len(self.pelaajat) + 1):
            vuorossa = self.pelaajat[(i + self.jakaja) % len(self.pelaajat)]  #Tää ei päivity näkymään nyt
            if vuorossa in self.mukanaPotissa:
                self.pelipoyta.paivitaNakymat()
                vuorossa.vaihtoja = self.pyydaVaihto(vuorossa)

        #panostuskierros vaihtojen jälkeen
        self.pelipoyta.pelivaihe = 3
        self.pelipoyta.paivitaNakymat()
        self.panostuskierros = PanostusKierros(self, self.pelipoyta)
        voittaja = self.panostuskierros.suoritaKierros()
        self.pelipoyta.paivitaNakymat()
        if voittaja:
            print("KAIKKI MUUT FOLDASI JA", voittaja.nimi, "voitti!")
            return [(haeVoittaja([voittaja]), self.potti)]

        self.pelipoyta.pelivaihe = 4
        self.pelipoyta.paivitaNakymat()
        self.kerroKortit() #Tää on vaan tulostus
        voittaja = self.vertaaKadet(self.mukanaPotissa) #Tää taitaa nyt olla vanha, alla tekee sen oikein
        voittajalista = self.jaaPotti()
        self.pelipoyta.paivitaNakymat()
        print("\nNO NYT on testattu voittajalistaa ja siihen tuli tämmöstä:", voittajalista)
        return (voittajalista)

    def autoKierros(self) -> list:
        self.pelipoyta.paivitaNakymat()
        self.keraaAlkupanokset()            
        self.jaaKortit()
        self.pelipoyta.paivitaNakymat()

        #Sitten kun voi automatisoida niin tähän väliin tulee:
        #panostuskierros 

        for i in range(1, len(self.pelaajat) + 1):
                    vuorossa = self.pelaajat[(i + self.jakaja) % len(self.pelaajat)]
                    if vuorossa in self.mukanaPotissa:
                        vuorossa.vaihtoja = self.pyydaVaihto(vuorossa)

        #Sitten kun voi automatisoida niin tähän väliin tulee:
        #panostuskierros                         
        
        self.pelipoyta.paivitaNakymat()
        self.kerroKortit()
        voittaja = self.vertaaKadet(self.mukanaPotissa)
        voittajalista = self.jaaPotti()
        print("")
        print("Voittaja:", voittaja)
        return (voittajalista)

    def keraaAlkupanokset(self): 
        for pelaaja in self.pelaajat:
            assert pelaaja.aktiivinen == True #Vain aktiiviset on mukana jakokierroksella
            if pelaaja.chips > self.alkupanos:
                pelaaja.chips -= self.alkupanos
                pelaaja.maksettuJakoon += self.alkupanos
                self.potti += self.alkupanos
            else:
                self.potti += pelaaja.chips
                pelaaja.maksettuJakoon += pelaaja.chips
                pelaaja.chips = 0
                pelaaja.allin = True


    def jaaKortit(self): 
        alkukadet = self.pakka.jaaKortit(len(self.pelaajat), 5)
        for i in range(len(alkukadet)):
            self.pelaajat[i].kasikortit = alkukadet[i]
    
    def kerroKortit(self):
        for pelaaja in self.pelaajat:
            print("Pelaaja:", pelaaja.nimi, "käsikortit: ", pelaaja.kasikortit)
        print ("Pakkaan jäi kortteja:", len(self.pakka.kortit))


    def vertaaKadet(self, pelaajat: list) -> list:  #Tarvitaanko mihinkään tätä funktiota välissä?
        aktiiviset = []
        for pelaaja in pelaajat:
            if pelaaja.aktiivinen: 
                aktiiviset.append(pelaaja)
        return haeVoittaja(aktiiviset)

    def jaaPotti(self) -> list:
        pottiaJaljella = self.potti
        voittajat = []  #Tallennetaan tupleen ([lista voittajista], näiden voittajien voittama potti)
        i = 0  #tuplen indeksi
        while pottiaJaljella > 0:  #Kun potti on jaettu kokonaan niin potin jakaminen pysähtyy
            voittaja = haeVoittaja(self.mukanaPotissa)  #voittaja on aina lista, vaikka voittajia olisi vain yksi. Hakee mukanaPotissa parhaa(n/t) kädet
            print("MILTÄ NÄYTTÄÄ NYT VOITTAJALISTA:", voittaja)
            for x in range(len(voittaja)):  #i:des voittajatuple, [0] on i:dennen tuplen voittajalista
                self.mukanaPotissa.remove(voittaja[x]["pelaaja"]) #x:s voittajatuple, [0] on x:nnen tuplen voittajalista, sen x:s voittaja
            voittajanPanostus = voittaja[0]["pelaaja"].maksettuJakoon
            tamaPotti = 0
            for y in range(len(self.pelaajat)):
                tamaPotti += min(voittajanPanostus, self.pelaajat[y].maksettuJakoon)  #Lisätään pottiin pelaajan y osuus
                self.pelaajat[y].maksettuJakoon -= min(voittajanPanostus, self.pelaajat[y].maksettuJakoon)  #Vähennetään voittoihin maksettu osuus pelaajan jäljellä olevista kontribuutioista loppupottiin
            pottiaJaljella -= tamaPotti  #Vähennetään osuus jäljellä olevasta potista
            voittajat.append((voittaja, tamaPotti))  #Lisätään voittajalistaan tuple: (voittaja(t), heidän kesken jaettava potti)
            print("Tästä voittokierroksesta maksettiin sivupottia", tamaPotti, "ja jäljelle jäi pottiin", pottiaJaljella)
            i+=1     

        return voittajat

    def pyydaVaihto(self, pelaaja: Pelaaja): #TÄHÄN sitten jotain, valitaan hiirellä, palauta lista. Funktio palauttaa vaihtojen lkm?
        while True:
            print("Vuorossa", pelaaja.nimi, "|| käsikortit: ", pelaaja.kasikortit)
            analysoitu = laskeArvot(pelaaja.kasikortit, vaihtoja=True)
            print("Kädessä on:", analysoitu["kasinimi"], "|| Vaihtosuosituksia:", analysoitu["vaihtosuositus"])
            vaihdettu = 0

            vaihdetaan = pelaaja.pyydaVaihdot()
            for Kortti in vaihdetaan:
                pelaaja.kasikortit.remove(Kortti)
                pelaaja.kasikortit.append(self.pakka.nosta())
                vaihdettu += 1

            return vaihdettu


