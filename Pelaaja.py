from AI.AI import randomAI, montecarloAI, steadycarloAI, superAI
from Pistelasku import laskeArvot
from GUI.GUI import GUI
from Pakka import Kortti

AI_TYYPIT = {
    "Satunnainen": randomAI,
    "Monte Carlo": montecarloAI,
    "steady": steadycarloAI,
    "Koneoppinut": superAI
}

class Pelaaja:
    '''Pelaaja-olio pitää kirjaa pelaajan tiedoista, valinnoista, pelivaiheista, sekä onko kyseessä AI vai ihmispelaaja.'''

    def __init__(self, nimi, tyyppi, AI_valinta=None, AI_asetukset=None):
        self.nimi: str = nimi
        self.tyyppi: str = tyyppi
        self.aktiivinen: bool = True

        self.nakyma: PelaajaNakyma
        self.gui: GUI

        if AI_valinta is not None:
            self.ai = AI_TYYPIT[AI_valinta](self, AI_asetukset)
            self.ai_tyyppi = AI_valinta
        else:
            self.ai = None

        self.kasikortit: list = []
        self.chips: int = 10000
        self.allin: bool = False
        self.folded: bool = False
        self.maksettuJakoon: int = 0
        self.maksettuPanostukseen: int = 0
        self.valinta: int = 0  # 1 = check/call, 2 = raise, 3 = big raise, 4 = fold
        self.vaihtoja: int | None = None
    
    def __str__(self):
        return f"{self.nimi}, {self.tyyppi}, stack: {self.chips}"

    def __repr__(self):
        return self.__str__()

    def toString(self):
        print(f"{self.nimi}, {self.tyyppi}, stack: {self.chips}")

    def nollaaKierros(self):
        '''Nollaa yksittäisen jaon tiedot'''

        self.kasikortit = []
        self.allin = False
        self.folded = False
        self.maksettuJakoon = 0
        self.vaihtoja = None
        if self.ai is not None:
            self.ai.nollaaKierros()

    def nollaaPanos(self):
        '''Nollaa panostuskierroksen tiedot'''

        self.maksettuPanostukseen = 0
        self.valinta = 0

    def nollaaKokoPeli(self):
        '''Nollaa koko pelin tiedot'''

        self.chips = 10000
        self.aktiivinen = True
        self.nollaaKierros()
        self.nollaaPanos()

    def tulostaKasi(self):
        print(f"Pelaaja {self.nimi}, käsikortit: {self.kasikortit}")

    def muokkaa(self, tiedot):
        '''Muokkaa pelaajaa saatujen tietojen perusteella, käytössä kun GUI:lta tulee muokkaus -komento.'''

        self.nimi = tiedot["nimi"]
        self.tyyppi = tiedot["tyyppi"]
        if tiedot["ai"] is not None:
            
            if tiedot["ai"] in ("Koneoppinut", "Koneoppinut 500k", "Koneoppinut 1M", "Koneoppinut 2M", "Koneoppinut 5M"): 
                luokka = "Koneoppinut" # Nämä kuuluisi oikeasti yhdeksi pääluokaksi ja malli pitäisi olla oma erillinen valinta GUI:ssa...
                malli = tiedot["ai"]
            else:
                luokka = tiedot["ai"]
                malli = None

            asetukset = {"aggressiivisuus": tiedot["ai_aggressiivisuus"], "luokka": luokka, "strategia": tiedot["ai_strategia"], "malli": malli}
            self.ai = AI_TYYPIT[luokka](self, asetukset)
            self.ai_tyyppi = tiedot["ai"]

    
    def pyydaPanostus(self, kierros=2) -> int:  #Onko tälle enää tarvetta, suoraan ohi?

        assert self.ai is not None

        return self.ai.pyydaPanostus(kierros)

    

class PelaajaNakyma:
    '''PelaajaNakymaan kerätään pelitilanteesta sellaiset luontaiset tiedot, jotka pelaajalla on tiedossa.
    Näkymää käytetään GUI:n pelitilanteen piirtämisessä, sekä valintojen tekemisessä, myös AI-pelaajilla.
    Ei sisällä arkaluontoista dataa, kuten täysiä pelaaja-olioita.'''

    def __init__(self, pelaaja, pelipoyta):

        self.nimi = pelaaja.nimi
        self.aktiivinen = pelaaja.aktiivinen

        self.kasikortit = pelaaja.kasikortit.copy()
        self.chips = pelaaja.chips
        self.allin = pelaaja.allin
        self.maksettuJakoon = pelaaja.maksettuJakoon
        self.maksettuPanostukseen = pelaaja.maksettuPanostukseen
        self.valinta = pelaaja.valinta  # 1 call, 2 raise, 3 big raise, 4 fold
        self.vaihtoja = pelaaja.vaihtoja

        self.pelivaihe = pelipoyta.pelivaihe  # 1 = 1. panostus | 2 = vaihdot | 3 = 2. panostus | 4 = showdown
        self.kierros = pelipoyta.kierros
        self.jakaja = pelipoyta.jakaja.nimi
        self.log = pelipoyta.log.copy()

        # Jaon ja panostuskierroksen tiedot kirjataan jos oliot ovat olemassa, muuten None  
        self.potti = None
        self.mukanaPotissa = None
        self.panos = None

        self.pelaajaVuorossa = None
        self.suurinKorotus = None
        self.maksettavaa = None
        self.pieniKorotus = None
        self.suuriKorotus = None
        self.folded = None

        if pelipoyta.jako is not None:
            self.potti = pelipoyta.jako.potti 
            self.panos = pelipoyta.jako.panos 
            self.folded = pelaaja.folded
            self.mukanaPotissa = [p.nimi for p in pelipoyta.jako.mukanaPotissa] #Ei pelaajaolioita viewiin, vain nimiä

            if pelipoyta.jako.panostuskierros is not None:
                self.pelaajaVuorossa = pelipoyta.jako.panostuskierros.pelaajaVuorossa.nimi
                self.suurinKorotus = pelipoyta.jako.panostuskierros.suurinKorotus
                self.maksettavaa = self.suurinKorotus - self.maksettuPanostukseen
                self.pieniKorotus = min(self.panos, self.chips - self.maksettavaa)
                self.suuriKorotus = min(3 * self.panos, self.chips - self.maksettavaa)

        #Listataan muut pelaajat niin, että järjestys vuorokierrossa säilyy, kun GUI:ssa Pelaaja on aina alhaalla
        omaIndex = pelipoyta.pelaajat.index(pelaaja)
        muidenJarjestys = pelipoyta.pelaajat[(omaIndex + 1) : ] + pelipoyta.pelaajat[ : omaIndex]
        self.muutPelaajat = []
        for pelaaja in muidenJarjestys:
            self.muutPelaajat.append(MuutNakee(pelaaja, pelipoyta))


    def to_dict(self):
        '''Muuntaa PelaajaNakyman verkkosiirtoa varten dict-muotoon.'''

        return {
            "nimi": self.nimi,
            "aktiivinen": self.aktiivinen,
            "kasikortit": [kortti.to_dict() for kortti in self.kasikortit],
            "chips": self.chips,
            "allin": self.allin,
            "maksettuJakoon": self.maksettuJakoon,
            "maksettuPanostukseen": self.maksettuPanostukseen,
            "valinta": self.valinta,
            "vaihtoja": self.vaihtoja,

            "pelivaihe": self.pelivaihe,
            "kierros": self.kierros,
            "jakaja": self.jakaja,
            "log": self.log.copy(),

            "potti": self.potti,
            "mukanaPotissa": (self.mukanaPotissa.copy() if self.mukanaPotissa is not None else None),
            "panos": self.panos,

            "pelaajaVuorossa": self.pelaajaVuorossa,
            "suurinKorotus": self.suurinKorotus,
            "maksettavaa": self.maksettavaa,
            "pieniKorotus": self.pieniKorotus,
            "suuriKorotus": self.suuriKorotus,
            "folded": self.folded,

            "muutPelaajat": [pelaaja.to_dict() for pelaaja in self.muutPelaajat]
        }

    @classmethod
    def from_dict(cls, data):
        '''Palauttaa verkkosiirrosta vastaanotetun dict-muotoisen PelaajaNakyman takaisin olioksi.'''

        obj = cls.__new__(cls)

        obj.nimi = data["nimi"]
        obj.aktiivinen = data["aktiivinen"]
        obj.kasikortit = [Kortti.from_dict(kortti) for kortti in data["kasikortit"]]
        obj.chips = data["chips"]
        obj.allin = data["allin"]
        obj.maksettuJakoon = data["maksettuJakoon"]
        obj.maksettuPanostukseen = data["maksettuPanostukseen"]
        obj.valinta = data["valinta"]
        obj.vaihtoja = data["vaihtoja"]

        obj.pelivaihe = data["pelivaihe"]
        obj.kierros = data["kierros"]
        obj.jakaja = data["jakaja"]
        obj.log = data["log"].copy()

        obj.potti = data["potti"]
        obj.mukanaPotissa = (data["mukanaPotissa"].copy() if data["mukanaPotissa"] is not None else None)
        obj.panos = data["panos"]

        obj.pelaajaVuorossa = data["pelaajaVuorossa"]
        obj.suurinKorotus = data["suurinKorotus"]
        obj.maksettavaa = data["maksettavaa"]
        obj.pieniKorotus = data["pieniKorotus"]
        obj.suuriKorotus = data["suuriKorotus"]
        obj.folded = data["folded"]

        obj.muutPelaajat = [MuutNakee.from_dict(pelaaja) for pelaaja in data["muutPelaajat"]]

        return obj
     

class MuutNakee:
    '''Luo pelaajasta sellaiset pelitiedot, jotka ovat muilla pöydän pelaajilla luontaisesti tiedossa.
    Ei sisällä arkaluontoista dataa, kuten käsikortteja (paitsi showdownissa, jolloin kortit paljastetaan).'''

    def __init__(self, pelaaja, pelipoyta):
        self.nimi = pelaaja.nimi
        self.tyyppi = pelaaja.tyyppi
        self.aktiivinen = pelaaja.aktiivinen
        self.chips = pelaaja.chips
        self.allin = pelaaja.allin
        self.folded = pelaaja.folded
        self.maksettuJakoon = pelaaja.maksettuJakoon
        self.maksettuPanostukseen = pelaaja.maksettuPanostukseen
        self.valinta = pelaaja.valinta
        self.vaihtoja = pelaaja.vaihtoja

        if pelipoyta.pelivaihe == 4:  #Showdownissa käsikortit näytetään
            self.kasikortit = pelaaja.kasikortit.copy()  
        elif pelaaja.kasikortit:
            self.kasikortit = [Kortti("muu", 0, alaspain = True) for _ in pelaaja.kasikortit]
        else: self.kasikortit = []

    def to_dict(self):
        '''Muuntaa olion dict-muotoon verkkosiirtoa varten.'''

        return {
            "nimi": self.nimi,
            "tyyppi": self.tyyppi,
            "aktiivinen": self.aktiivinen,
            "chips": self.chips,
            "allin": self.allin,
            "folded": self.folded,
            "maksettuJakoon": self.maksettuJakoon,
            "maksettuPanostukseen": self.maksettuPanostukseen,
            "valinta": self.valinta,
            "vaihtoja": self.vaihtoja,
            "kasikortit": [kortti.to_dict() for kortti in self.kasikortit]
        }

    @classmethod
    def from_dict(cls, data):
        '''Palauttaa verkkosiirrosta vastaanotetun dictin olioksi.'''

        obj = cls.__new__(cls)

        obj.nimi = data["nimi"]
        obj.tyyppi = data["tyyppi"]
        obj.aktiivinen = data["aktiivinen"]
        obj.chips = data["chips"]
        obj.allin = data["allin"]
        obj.folded = data["folded"]
        obj.maksettuJakoon = data["maksettuJakoon"]
        obj.maksettuPanostukseen = data["maksettuPanostukseen"]
        obj.valinta = data["valinta"]
        obj.vaihtoja = data["vaihtoja"]
        obj.kasikortit = [Kortti.from_dict(kortti) for kortti in data["kasikortit"]]

        return obj

        