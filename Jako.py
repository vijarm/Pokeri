from Pistelasku import laskeArvot, haeVoittaja
from Pelaaja import Pelaaja
from Panostus import PanostusKierros

class Jako:
    '''Pelin yksittäinen jako, jossa käsitellään pelin kulku ja tilat korttien jaosta kierroksen voittajan löytymiseen saakka.'''

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
        self.vaihtoindeksit: list | None = None

        self.fold_voitto = False
        self.pottiaJaljella = 0
        self.showdownOdottaa = True if self.pelipoyta.simulointi is None else False
        self.showdownValmis = False
        self.voittajalista = []

        self.tila = "alku"
        self.tulos = None

        self.pakka.sekoita()


    def paivitaTila(self):
        '''Päivittää jaon tilan etenemistä, aloitus -> panostus1 -> vaihdot -> panostus2 -> showdown'''
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


    def aloitaJako(self):
        '''Aloittaa jaon, kerää mukana olevilta pelaajilta alkupanokset ja jakaa kortit.'''

        assert len(self.pelaajat) >= 2, "Pelin ei kuulu siirtyä jakoon jos aktiivisia pelaajia on vähemmän kuin 2"
        self.pelipoyta.pelivaihe = 0
        self.pelipoyta.paivitaNakymat()
        self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "yleisilmoitus", "ilmoitus": ["Uusi kierros alkaa!", f"Alkupanos {self.panos} merkkiä.", "Kerätään panokset ja jaetaan kortit!"]})

        for p in self.pelaajat: #Tämä tarvitaan Q-learning aikana, muuten voi ottaa pois
            if p.ai is not None and p.ai.luokka == "Koneoppinut":
                p.ai.chips_jaon_alussa = p.chips

        self.keraaAlkupanokset()

        self.jaaKortit()
        self.pelipoyta.paivitaNakymat()
        self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "jaaKortit"})

        self.pelipoyta.pelivaihe = 1
        self.panostuskierros = PanostusKierros(self, self.pelipoyta, kierros=1)
        self.tila = "panostus1"


    def keraaAlkupanokset(self): 
        '''Kerää pelaajilta alkupanokset, muuttaa pelaajan all-in tilaan jos kaikki pelimerkit maksetaan alkupanoksessa.'''

        for pelaaja in self.pelaajat:
            assert pelaaja.aktiivinen == True #Vain aktiiviset on mukana jakokierroksella

            if pelaaja.chips > self.panos:
                pelaaja.chips -= self.panos
                pelaaja.maksettuJakoon += self.panos
                self.potti += self.panos

            else:  #Jos pelaaja menee all-in alkupanoksen vuoksi
                self.potti += pelaaja.chips
                pelaaja.maksettuJakoon += pelaaja.chips
                pelaaja.chips = 0
                pelaaja.allin = True
                self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "pelaajailmoitus", "pelaaja": pelaaja.nimi, "ilmoitus": "ALL-IN!"})

        #Tarkistetaanko onko joku maksanut "liikaa" -> palautetaan ylimääräinen
        SuurinPanosEnsin = sorted(self.pelaajat, key=lambda p: p.maksettuJakoon, reverse=True)
        maksettuLiikaa = SuurinPanosEnsin[0].maksettuJakoon - SuurinPanosEnsin[1].maksettuJakoon
        if maksettuLiikaa != 0:
            #print("PALAUTETAAN LIIKAA MAKSETTU PELAAJALLE,", SuurinPanosEnsin[0].nimi, "yhteensä:", maksettuLiikaa)
            self.potti -= maksettuLiikaa  #Vähennetään potista ja pelaajan kontribuutio-tiedoista, lisätään chipit stackiin.
            SuurinPanosEnsin[0].maksettuJakoon -= maksettuLiikaa
            SuurinPanosEnsin[0].chips += maksettuLiikaa


    def jaaKortit(self): 
        '''Jaetaan jokaiselle pelaajalle 5 aloituskorttia.'''

        alkukadet = self.pakka.jaaKortit(len(self.pelaajat), 5)
        for i in range(len(alkukadet)):
            self.pelaajat[i].kasikortit = alkukadet[i]
            if self.pelaajat[i].ai is not None:  # AI pelaajille tehdään heti käden analysointi ja annetaan vaihtosuositukset
                self.pelaajat[i].ai.kasidata = laskeArvot(self.pelaajat[i].kasikortit, vaihtoja = True)
    
    def kerroKortit(self):
        '''Tulostaa käsikortit konsoliin, debuggaukseen'''
        for pelaaja in self.pelaajat:
            print("Pelaaja:", pelaaja.nimi, "käsikortit: ", pelaaja.kasikortit)
        print ("Pakkaan jäi kortteja:", len(self.pakka.kortit))


    def vertaaKadet(self, pelaajat: list) -> list:  #Tarvitaanko mihinkään tätä funktiota välissä?
        '''Kutsuu aktiivisien pelaajien listalla pistelaskun haeVoittaja-funktiota, ja palauttaa vertailussa parhaan käden omaavan pelaajan.'''

        aktiiviset = []
        for pelaaja in pelaajat:
            if pelaaja.aktiivinen: 
                aktiiviset.append(pelaaja)
        return haeVoittaja(aktiiviset)


    def pyydaVaihtoAI(self, pelaaja: Pelaaja): 
        '''Pyytää tietokonepelaajan ai-luokalta vaihdettavia kortteja. Vaihtaa vastauksena saadut kortit.'''

        #print("Vuorossa", pelaaja.nimi, "|| käsikortit: ", pelaaja.kasikortit)
        assert pelaaja.ai is not None, "AI:n vaihtofunktioon ohjataan vain AI pelaajat"
        analysoitu = pelaaja.ai.kasidata
        #print("Kädessä on:", analysoitu["kasinimi"], "|| Vaihtosuosituksia:", analysoitu["vaihtosuositus"])
        vaihdettu = 0

        assert pelaaja.ai is not None, "ihmispelaaja ohjattiin AI-pelaajan vaihtofunktioon"

        vaihdetaan = pelaaja.ai.vaihdaKortit()  #Indexit jotta animaatio osuu oikeaan korttiin?
        vaihtoindeksit = []

        if self.pelipoyta.simulointi is None:  #vaihtoindeksit GUI:ta varten
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
        '''Seuraa vaihtovuorojen tilaa, tietokonepelaajat vaihtavat suoraan ja ihmispelaajan kohdalla lähetetään GUI:lle pyyntö vaihdoista.
        Siirtää ihmispelaajalta tulleen vaihtopyynnön käsiteltäväksi kun päätös on tullut GUI:sta komennolla.'''

        self.pelipoyta.pelivaihe = 2

        if self.vaihtoOdottaa:
            assert self.vaihtoPelaaja is not None
            
            if self.vaihtoindeksit is None:
                return

            self.vastaanotaVaihdot(self.vaihtoindeksit)  #GUI:ssa valinta on tehty jos ei ollut None
            self.vaihtoindeksit = None
            return

        self.pelipoyta.paivitaNakymat()

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
        self.pelipoyta.paivitaNakymat()
        self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "pyydaVaihdot", "pelaaja": vuorossa.nimi})
        return


    def vastaanotaVaihdot(self, vaihtoindeksit): 
        '''Käsittelee ihmispelaajalta GUI:sta tulleen vaihtopäätöksen, poistaa vaihdettavat kortit ja nostaa uudet.'''

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
        '''Käynnistää showdown-vaiheen, ilmoittaa GUI:lle showdownin alkamisesta.'''

        self.pelipoyta.pelivaihe = 4
        self.pottiaJaljella = self.potti
        self.voittajalista = []

        self.pelipoyta.paivitaNakymat()
        self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "aloitaShowdown"})
        if self.pelipoyta.simulointi is None:
            self.showdownOdottaa = True  


    def paivitaShowdown(self):
        '''Päivittää showdownin tilaa. Odottaa tarvittaessa ihmispelaajan ok -kuittausta GUI:sta.
        Jatkaa showdown-tilassa kunnes koko potti on jaettu. Lisää voittajalistaan voittaneet pelaajat sekä voitetun potin.'''

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

        if self.pelipoyta.simulointi is None:
            self.showdownOdottaa = True
        

