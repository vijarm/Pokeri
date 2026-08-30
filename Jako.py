from Pistelasku import laskeArvot, haeVoittaja
from Pelaaja import Pelaaja
from Panostus import PanostusKierros

class Jako:
    def __init__(self, pelipoyta):
        self.pelipoyta = pelipoyta
        self.pakka = pelipoyta.pelipakka
        self.pelaajat = [p for p in pelipoyta.pelaajat if p.aktiivinen and p.chips > 0]
        self.mukanaPotissa = self.pelaajat.copy()
        self.potti = 0
        self.panos = pelipoyta.panos
        self.jakaja = self.pelaajat.index(pelipoyta.jakaja) #Jakajan indeksi pelaajalistasta
        self.panostuskierros = None
        
        self.vaihtoVuoro = 1
        self.vaihtoOdottaa = False
        self.vaihtoPelaaja = None
        self.vaihtoindeksit = None

        self.pottiaJaljella = 0
        self.showdownOdottaa = True if self.pelipoyta.simulointi == False else False
        self.showdownValmis = False
        self.voittajalista = []

        self.tila = "alku"
        self.tulos = None

        self.pakka.sekoita()


    #Jakokierroksen päälooppi läpi, jako -> panostus1 -> vaihdot -> panostus2 -> showdown
    def paivitaTila(self):
        if self.tila == "alku":
            self.aloitaJako()

        elif self.tila == "panostus1":
            assert self.panostuskierros is not None
            self.panostuskierros.paivitaTila()

            if self.panostuskierros.odottaaValintaa:
                return

            if not self.panostuskierros.valmis:
                return

            if self.panostuskierros.voittaja is not None:
                self.tulos = [(haeVoittaja([self.panostuskierros.voittaja]), self.potti)]
                self.tila = "valmis" 
                return

            self.tila = "vaihdot"

        elif self.tila == "vaihdot":
            self.paivitaVaihdot()

        elif self.tila == "panostus2":
            assert self.panostuskierros is not None
            self.panostuskierros.paivitaTila()

            if self.panostuskierros.odottaaValintaa:
                return

            if not self.panostuskierros.valmis:
                return

            if self.panostuskierros.voittaja is not None:
                self.tulos = [(haeVoittaja([self.panostuskierros.voittaja]), self.potti)]
                self.tila = "valmis"
                return

            self.tila = "showdown"
            self.aloitaShowdown()

        elif self.tila == "showdown":
            self.paivitaShowdown()



    '''
    def pelaaKierros(self) -> list:
        assert len(self.pelaajat) >= 2, "Pelin ei kuulu siirtyä jakoon jos aktiivisia pelaajia on vähemmän kuin 2"
        self.keraaAlkupanokset()       
        self.pelipoyta.paivitaNakymat()  #Myös tässä välissä jos tulee joku all-in trigger tms?     
        self.jaaKortit()
        self.pelipoyta.paivitaNakymat()

        #panostuskierros ennen vaihtoja
        self.pelipoyta.pelivaihe = 1
        self.panostuskierros = PanostusKierros(self, self.pelipoyta, kierros=1)
        self.pelipoyta.paivitaNakymat()
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
        self.pelipoyta.paivitaNakymat()
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
    '''

    def aloitaJako(self):
        assert len(self.pelaajat) >= 2, "Pelin ei kuulu siirtyä jakoon jos aktiivisia pelaajia on vähemmän kuin 2"
        self.pelipoyta.pelivaihe = 0
        self.pelipoyta.paivitaNakymat()
        self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "yleisilmoitus", "ilmoitus": ["Uusi kierros alkaa!", f"Alkupanos {self.panos} merkkiä.", "Kerätään panokset ja jaetaan kortit!"]})
        self.keraaAlkupanokset()

        self.jaaKortit()
        self.pelipoyta.paivitaNakymat()
        self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "jaaKortit"})

        self.pelipoyta.pelivaihe = 1
        self.panostuskierros = PanostusKierros(self, self.pelipoyta, kierros=1)
        self.tila = "panostus1"

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
                vuorossa.vaihtoja = self.pyydaVaihtoAI(vuorossa)

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
            if pelaaja.chips > self.panos:
                pelaaja.chips -= self.panos
                pelaaja.maksettuJakoon += self.panos
                self.potti += self.panos
            else:
                self.potti += pelaaja.chips
                pelaaja.maksettuJakoon += pelaaja.chips
                pelaaja.chips = 0
                pelaaja.allin = True
                self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "pelaajailmoitus", "pelaaja": pelaaja.nimi, "ilmoitus": "ALL-IN!"})

        #Tarkistetaanko onko joku maksanut "liikaa" -> palautetaan ylimääräinen
        SuurinPanosEnsin = sorted(self.pelaajat, key=lambda p: p.maksettuJakoon, reverse=True)
        maksettuLiikaa = SuurinPanosEnsin[0].maksettuJakoon - SuurinPanosEnsin[1].maksettuJakoon
        if maksettuLiikaa != 0:
            print("PALAUTETAAN LIIKAA MAKSETTU PELAAJALLE,", SuurinPanosEnsin[0].nimi, "yhteensä:", maksettuLiikaa)
            self.potti -= maksettuLiikaa  #Vähennetään potista ja pelaajan kontribuutio-tiedoista, lisätään chipit stackiin.
            SuurinPanosEnsin[0].maksettuJakoon -= maksettuLiikaa
            SuurinPanosEnsin[0].chips += maksettuLiikaa


    def jaaKortit(self): 
        alkukadet = self.pakka.jaaKortit(len(self.pelaajat), 5)
        for i in range(len(alkukadet)):
            self.pelaajat[i].kasikortit = alkukadet[i]
            if self.pelaajat[i].ai is not None:  # AI pelaajille tehdään heti käden analysointi ja annetaan vaihtosuositukset
                self.pelaajat[i].ai.kasidata = laskeArvot(self.pelaajat[i].kasikortit, vaihtoja = True)
    
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

    '''def jaaPotti(self) -> list:
        pottiaJaljella = self.potti
        voittajat = []  #Tallennetaan tupleen ([lista voittajista], näiden voittajien voittama potti)
        i = 0  #tuplen indeksi

        while pottiaJaljella > 0:  #Kun potti on jaettu kokonaan niin potin jakaminen pysähtyy
            assert len(self.mukanaPotissa) > 0, "Viimeistä pottia jakamassa täytyy olla jokin pelaaja"
            voittaja = haeVoittaja(self.mukanaPotissa)  #voittaja on aina lista, vaikka voittajia olisi vain yksi. Hakee mukanaPotissa parhaa(n/t) kädet
            print("MILTÄ NÄYTTÄÄ NYT VOITTAJALISTA:", voittaja)
#            for x in range(len(voittaja)):  #i:des voittajatuple, [0] on i:dennen tuplen voittajalista
#                self.mukanaPotissa.remove(voittaja[x]["pelaaja"]) #x:s voittajatuple, [0] on x:nnen tuplen voittajalista, sen x:s voittaja
            voittajanPanostus = voittaja[0]["pelaaja"].maksettuJakoon

            for p in self.mukanaPotissa:
                print("PELAAJA", p.nimi, "maksanut", p.maksettuJakoon)
            self.mukanaPotissa = [p for p in self.mukanaPotissa if p.maksettuJakoon > voittajanPanostus]  #Voitonjaossa jatkavat vain ne pelaajat, jotka ovat maksaneet pottiin enemmän kuin viimeisen potin voittanut

            for p in self.mukanaPotissa:
                print("PELAAJA", p.nimi, "maksanut", p.maksettuJakoon)
            tamaPotti = 0
            for y in range(len(self.pelaajat)):
                tamaPotti += min(voittajanPanostus, self.pelaajat[y].maksettuJakoon)  #Lisätään pottiin pelaajan y osuus
                self.pelaajat[y].maksettuJakoon -= min(voittajanPanostus, self.pelaajat[y].maksettuJakoon)  #Vähennetään voittoihin maksettu osuus pelaajan jäljellä olevista kontribuutioista loppupottiin
            pottiaJaljella -= tamaPotti  #Vähennetään osuus jäljellä olevasta potista
            voittajat.append((voittaja, tamaPotti))  #Lisätään voittajalistaan tuple: (voittaja(t), heidän kesken jaettava potti)
            print("Tästä voittokierroksesta maksettiin sivupottia", tamaPotti, "ja jäljelle jäi pottiin", pottiaJaljella, "mukana vielä", self.mukanaPotissa)
            i+=1     

            for p in self.pelaajat:  # ei tietenkään lopullisesti näin koska tämä käy pelaajat yksitellen?
                if p.ai is None:
                    p.gui.GUI_pelipoyta.valintapaneeli.mode = "showdown"
                    
                    while p.gui.GUI_pelipoyta.valintapaneeli.jatketaan is None:
                        p.gui.process_events()
                        p.gui.draw()
                        p.gui.clock.tick(60)  #FPS

                    p.gui.GUI_pelipoyta.valintapaneeli.get_valinta()

        return voittajat'''

    def pyydaVaihtoAI(self, pelaaja: Pelaaja): 

        print("Vuorossa", pelaaja.nimi, "|| käsikortit: ", pelaaja.kasikortit)
        analysoitu = laskeArvot(pelaaja.kasikortit, vaihtoja=True)
        print("Kädessä on:", analysoitu["kasinimi"], "|| Vaihtosuosituksia:", analysoitu["vaihtosuositus"])
        vaihdettu = 0

        assert pelaaja.ai is not None, "ihmispelaaja ohjattiin AI-pelaajan vaihtofunktioon"

        vaihdetaan = pelaaja.ai.vaihdaKortit()  #Indexit jotta animaatio osuu oikeaan korttiin?
        vaihtoindeksit = []

        if self.pelipoyta.simulointi is False:  #vaihtoindeksit GUI:ta varten
            vaihtoindeksit = [i for i, kasikortti in enumerate(pelaaja.kasikortit) if kasikortti in vaihdetaan]

        for Kortti in vaihdetaan:
            pelaaja.kasikortit.remove(Kortti)
            pelaaja.kasikortit.append(self.pakka.nosta())
            vaihdettu += 1

        self.pelipoyta.loggaa(f"{pelaaja.nimi} vaihtoi {vaihdettu} korttia.")
        self.pelipoyta.paivitaNakymat()
        self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "korttivaihto", "pelaaja": pelaaja.nimi, "vaihtoindeksit": vaihtoindeksit})

        return vaihdettu

    def paivitaVaihdot(self):
        self.pelipoyta.pelivaihe = 2
        self.pelipoyta.paivitaNakymat()

        if self.vaihtoOdottaa:
            assert self.vaihtoPelaaja is not None
            
            if self.vaihtoindeksit is None:
                return

            self.vastaanotaVaihdot(self.vaihtoindeksit)  #GUI:ssa valinta on tehty jos ei ollut None
            self.vaihtoindeksit = None
            return

        if self.vaihtoVuoro > len(self.pelaajat):  #Kaikki pelaajat ovat vaihtaneet, siirrytään seuraavaan vaiheeseen
            self.pelipoyta.pelivaihe = 3
            self.panostuskierros = PanostusKierros(self, self.pelipoyta, kierros=2)
            self.tila = "panostus2"
            return

        vuorossa = self.pelaajat[(self.vaihtoVuoro + self.jakaja) % len(self.pelaajat)]  #Haetaan seuraava vuorossa oleva pelaaja

        if vuorossa not in self.mukanaPotissa:
            self.vaihtoVuoro += 1
            return

        if vuorossa.ai is not None:
            vuorossa.vaihtoja = self.pyydaVaihtoAI(vuorossa)
            self.vaihtoVuoro += 1
            return

        #Ihmispelaajan vuoro
        self.vaihtoOdottaa = True
        self.vaihtoPelaaja = vuorossa
        self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "pyydaVaihdot", "pelaaja": vuorossa.nimi})
        return


    def vastaanotaVaihdot(self, vaihtoindeksit):  #ihmispelaajan vaihdot
        assert self.vaihtoOdottaa
        assert self.vaihtoPelaaja is not None

        pelaaja = self.vaihtoPelaaja
        vaihdetaan = [pelaaja.kasikortit[i] for i in vaihtoindeksit]

        for kortti in vaihdetaan:
            pelaaja.kasikortit.remove(kortti)
            pelaaja.kasikortit.append(self.pakka.nosta())

        pelaaja.vaihtoja = len(vaihdetaan)
        self.pelipoyta.loggaa(f"{pelaaja.nimi} vaihtoi {pelaaja.vaihtoja} korttia.")
        self.pelipoyta.paivitaNakymat()
        self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "korttivaihto", "pelaaja": pelaaja.nimi, "vaihtoindeksit": vaihtoindeksit})

        self.vaihtoVuoro += 1
        self.vaihtoOdottaa = False
        self.vaihtoPelaaja = None


    def aloitaShowdown(self):
        self.pelipoyta.pelivaihe = 4
        self.pottiaJaljella = self.potti
        self.voittajalista = []

        self.pelipoyta.paivitaNakymat()
        self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "aloitaShowdown"})
        if self.pelipoyta.simulointi == False:
            self.showdownOdottaa = True  

    def paivitaShowdown(self):
        #ihmispelaaja = next(p for p in self.pelipoyta.pelaajat if p.ai is None)  #Tää on jo poistettu?

        if self.showdownOdottaa:

            if not self.pelipoyta.ok:
                return
            
            self.pelipoyta.ok = False
            self.showdownOdottaa = False
            return

        if self.pottiaJaljella <= 0:
            self.tulos = self.voittajalista
            self.tila = "valmis"
            return

        assert len(self.mukanaPotissa) > 0, "Viimeistä pottia jakamassa täytyy olla jokin pelaaja"
        voittaja = haeVoittaja(self.mukanaPotissa)  #voittaja on aina lista, vaikka voittajia olisi vain yksi. Hakee mukanaPotissa parhaa(n/t) kädet

        voittajanPanostus = voittaja[0]["pelaaja"].maksettuJakoon
        self.mukanaPotissa = [p for p in self.mukanaPotissa if p.maksettuJakoon > voittajanPanostus]  #Voitonjaossa jatkavat vain ne pelaajat, jotka ovat maksaneet pottiin enemmän kuin viimeisen potin voittanut

        tamaPotti = 0
        for pelaaja in self.pelaajat:
            osuus = min(voittajanPanostus, pelaaja.maksettuJakoon)
            tamaPotti += osuus  #Lisätään pottiin pelaajan osuus
            pelaaja.maksettuJakoon -= osuus  #Vähennetään voittoihin maksettu osuus pelaajan jäljellä olevista kontribuutioista loppupottiin

        self.pottiaJaljella -= tamaPotti  #Vähennetään osuus jäljellä olevasta potista
        self.voittajalista.append( (voittaja, tamaPotti) )
        self.pelipoyta.loggaa(f"{voittaja[0]["pelaaja"].nimi} voitti potin: {tamaPotti} merkkiä!")

        showdownData = {
            "kasikortit": voittaja[0]["pelaaja"].kasikortit,
            "kasinimi": voittaja[0]["kasinimi"],
            "voittaja": voittaja[0]["pelaaja"].nimi,
            "potti": tamaPotti,
            "pottiaJaljella": self.pottiaJaljella,
        }

        self.pelipoyta.paivitaNakymat()
        self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "showdownData", "showdownData": showdownData})

        if self.pelipoyta.simulointi == False:
            self.showdownOdottaa = True
        

