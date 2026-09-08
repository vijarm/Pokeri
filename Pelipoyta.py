from Pakka import Pakka
from Pelaaja import Pelaaja, PelaajaNakyma
from Jako import Jako
from Pistelasku import haeVoittaja
from random import randint

class Pelipoyta:
    '''Pelipoyta on käynnissä olevan pelin uloin tilakone. Seuraa pelin kulkua läpi jakojen,
    aloittaa ja lopettaa yksittäiset jaot, ja lopettaa koko pelin jos pelaajia on jäljellä enää yksi.
    Jos peliä pelataan simulointi-modella, kerää tilastoja simulointi-olion tietoihin.'''

    def __init__(self, pelaajat: list, paivitys_to_gui=None, simulointi=None):
        self.PerusPakka = Pakka()
        self.PerusPakka.luo_pakka()

        self.pelipakka = Pakka()
        self.pelipakka.kortit = self.PerusPakka.kortit.copy()

        self.paivitys_to_gui = paivitys_to_gui
        
        self.pelaajat = pelaajat
        self.kierros: int = 0
        self.jakovuoro: int = randint(0, len(pelaajat) - 1)  #Ensimmäinen jakaja arvotaan
        self.jakaja: Pelaaja = self.pelaajat[self.jakovuoro % len(self.pelaajat)]
        self.panos: int = 0

        self.pelivaihe = 0  # 0 = alku | 1 = 1. panostus | 2 = vaihdot | 3 = 2. panostus | 4 = showdown
        self.jako = None
        self.tila = "peli"
        self.voittaja = None
        self.ok = False  #Yleinen "ok" kuittaus GUI:sta

        self.simulointi = simulointi
        self.log = []
    

    def paivitaTila(self):
        '''Pelipöydän tilan päivitys, aloittaa ja lopettaa jaot, sekä päättää koko pelin jos pelaajia on jäljellä vain 1.'''

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

                   
    def uusiKierros(self): 
        '''Aloittaa uuden kierroksen. Lähettää uuteen jakoon pelaajat, jotka ovat vielä pelissä mukana.'''
        aktiiviset = [p for p in self.pelaajat if p.aktiivinen and p.chips > 0]  #Vain aktiiviset pelaa, lisävarmistus chips > 0
        if len(aktiiviset) < 2: pass #Tämän ei pitäisi toteutua, muuta assert?

        self.kierros += 1
        self.paivitaJakaja()
        self.paivitaPanos()
        
        self.jako = Jako(self)


    def kasitteleJakoTulos(self):
        '''Käsittelee Jako-oliolta muodostuneen tuloksen. Jakaa potissa olevat chipsit pelaajille niiden oikeuttaman osuuden mukaisesti,
        kerää statistiikkaa jos simulointi-mode on päällä, ja suorittaa koneoppivan AI:n palkintojen jaon, jos AI on koulutuksessa.'''

        assert self.jako is not None
        tulos = self.jako.tulos
        assert isinstance(tulos, list)
        #tulos[x] = voittotuplen indeksi, jos potteja on useita niin x > 1
        #tulos[x][0] = x:n voittopotin voittajapelaajat LISTA, tulos[x][1] = x:n voittopotin summa (int)
        #tulos[x][0][y] = x:n voittopotin voittajapelaajien y:s voittajapelaaja
        for x in range(len(tulos)):
            for y in range(len(tulos[x][0])):
                tulos[x][0][y]["pelaaja"].chips += (tulos[x][1] // len(tulos[x][0]))

        if self.simulointi is not None:
            voittaja = tulos[0][0][0]["pelaaja"]  #suurimman potin ensimmäinen voittaja
            self.simulointi.pelatutKadet += 1
            if self.jako.fold_voitto == True:
                self.simulointi.fold_voitot[voittaja] += 1
            else:
                if len(tulos[0][0]) > 1:  #Suurin potti tasapeli
                    self.simulointi.tasapelit += 1

                self.simulointi.kasivoitot[voittaja] += 1
                self.simulointi.voittokadet[tulos[0][0][0]["voittoArvio"][0]] += 1  #Voittajan käsi 0-17

                #Parhaan häviävän käden hakeminen
                ilmanvoittajaa = [p for p in self.jako.pelaajat if p != tulos[0][0][0]["pelaaja"] and not p.folded]
                parashaviaja = self.jako.vertaaKadet(ilmanvoittajaa)
                luokka = parashaviaja[0]["voittoArvio"][0]
                self.simulointi.parasHaviaja[luokka] += 1

        #Tarvitaan vain Koneoppinut -ai:n koulutuksessa
        for pelaaja in self.jako.pelaajat:  
            if pelaaja.ai is not None and pelaaja.ai.luokka == "Koneoppinut":
                ai = pelaaja.ai
                reward = (pelaaja.chips - ai.chips_jaon_alussa) / 100

                for i, (state, valinta) in enumerate(reversed(ai.paatokset)):
                    paino = ai.lambda_kerroin ** i
                    ai.update(state, valinta, reward * paino)

                ai.paatokset = []
                ai.chips_jaon_alussa = None
                ai.koulutetut_jaot += 1

                #if ai.koulutetut_jaot == 10000000:  #Seuraava pysyvä malli 10M kättä
                #    ai.tallenna("models/ai_10m.pkl")

                #if ai.koulutetut_jaot % 100000 == 0: #Jatkuva tallennus 100k käden jälkeen
                #    ai.tallenna("models/ai_jatkuva.pkl")
                #    print("TALLENNETTU Q-TABLE TIEDOSTOON, jakoja koulutettu", ai.koulutetut_jaot)



        self.lopetaKierros()
        self.paivitaNakymat()
        self.paivitaGUI("pelipoyta", {"tapahtuma": "pottiJaettu"})  #Tällä ei ole mitään vastatapahtumaa, halutaanko joku yhteisveto tilanteesta?
        self.jako = None


    def lopetaKierros(self): 
        '''Lopettaa viimeisen jaon, nollaa pelaajat ja pakan, ja tiputtaa pois pelaajat, joiden pelimerkit ovat loppuneet.'''

        for pelaaja in self.pelaajat:
            pelaaja.nollaaKierros()
            if pelaaja.aktiivinen:
                if pelaaja.chips <= 0:
                    pelaaja.aktiivinen = False
                    self.paivitaNakymat()
                    self.loggaa(f"{pelaaja.nimi} tippui pelistä!")
                    self.paivitaGUI("pelipoyta", {"tapahtuma": "pelaajaTippui", "pelaaja": pelaaja.nimi, "ilmoitus": [f"{pelaaja.nimi} tippui pelistä!"]})

        self.pelipakka.kortit.clear()
        self.pelipakka.kortit = self.PerusPakka.kortit.copy()

    def julistaVoittaja(self, voittaja: Pelaaja):
        '''Ilmoittaa GUI:lle kun koko pelin voittaja on löytynyt.'''

        self.paivitaNakymat()
        self.loggaa(f"{voittaja.nimi} voitti koko pelin!")
        self.paivitaGUI("pelipoyta", {"tapahtuma": "voittajaLoytyi", "pelaaja": voittaja.nimi, "ilmoitus": ["Peli on päättynyt!", f"Pelin on voittanut {voittaja.nimi}!"]})
        #print("TÖTTÖRÖÖ, VOITTAJA ON ", voittaja.nimi, "JA PEITTOSI MUUT KERÄÄMÄLLÄ", voittaja.chips, "CHIPPIÄ!")

    def paivitaJakaja(self): 
        '''Päivittää jakajan vuoron oikein vuorojärjestyksessä.'''

        while True:
            self.jakovuoro += 1
            if self.pelaajat[self.jakovuoro % len(self.pelaajat)].aktiivinen == False:
                continue
            else: 
                self.jakaja = self.pelaajat[self.jakovuoro % len(self.pelaajat)]
                break

    def paivitaPanos(self):
        '''Päivittää panosta joka 4. kierros, panos kasvaa voimakkaammin pelin edetessä.'''

        if self.kierros < 13:  #kierrokset 1-12, +50 joka 4. kierros
            self.panos = 100 + (50 * ((self.kierros - 1) // 4))
        elif (self.kierros - 1) % 4 == 0:
            if self.kierros > 28: #kierros > 29, +400 joka 4. kierros
                self.panos += 400
            elif self.kierros < 21: #kierroksilla 13 ja 17 +100
                self.panos += 100
            else:
                self.panos += 200 #väliin jäävillä 21 ja 25 +200

    def loggaa(self, teksti: str):
        '''Lisää logiin tiedon pelitapahtumasta.'''

        if self.simulointi is None:
            self.log.append(teksti)


    def paivitaNakymat(self):  
        '''Luo jokaiselle pelaajalle uuden päivitetyn PelaajaNakyma -olion'''

        for pelaaja in self.pelaajat:
            pelaaja.nakyma = PelaajaNakyma(pelaaja, self)
            #print("Ovat samoja:", pelaaja.nakyma.to_dict() == PelaajaNakyma.from_dict(pelaaja.nakyma.to_dict()).to_dict())
            

    def paivitaGUI(self, tyyppi, tiedot):  
        '''Luo GUI:lle lähetettävän päivityksen uudesta pelitilanteesta / -tapahtumasta'''

        if self.simulointi is None:
            for pelaaja in self.pelaajat:
                if pelaaja.ai is None:
                    assert self.paivitys_to_gui is not None, "GUI päivitys tarvitsee paivitys_to_gui funktion"
                    self.paivitys_to_gui(pelaaja, tyyppi, tiedot, pelaaja.nakyma)

