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
        self.valinta: int = 0  # 1 = check/call, 2 = raise, 3 = fold
        self.vaihtoja: int | None = None
    
    def __str__(self):
        return f"{self.nimi}, {self.tyyppi}, stack: {self.chips}"

    def __repr__(self):
        return self.__str__()

    def toString(self):
        print(f"{self.nimi}, {self.tyyppi}, stack: {self.chips}")

    def nollaaKierros(self):
        self.kasikortit = []
        self.allin = False
        self.folded = False
        self.maksettuJakoon = 0
        self.vaihtoja = None
        if self.ai is not None:
            self.ai.nollaaKierros()

    def nollaaPanos(self):
        self.maksettuPanostukseen = 0
        self.valinta = 0

    def nollaaKokoPeli(self):
        self.chips = 10000
        self.aktiivinen = True
        self.nollaaKierros()
        self.nollaaPanos()

    def tulostaKasi(self):
        print(f"Pelaaja {self.nimi}, käsikortit: {self.kasikortit}")

    def muokkaa(self, tiedot):
        self.nimi = tiedot["nimi"]
        self.tyyppi = tiedot["tyyppi"]
        if tiedot["ai"] is not None:
            ai_luokka = AI_TYYPIT[tiedot["ai"]]
            asetukset = {"aggressiivisuus": tiedot["ai_aggressiivisuus"], "luokka": tiedot["ai"], "strategia": tiedot["ai_strategia"]}
            self.ai = ai_luokka(self, asetukset)
            self.ai_tyyppi = tiedot["ai"]


    
    def pyydaPanostus(self, kierros=2) -> int:  #Onko tälle enää tarvetta, suoraan ohi?

        assert self.ai is not None

        return self.ai.pyydaPanostus(kierros)

    
    def pyydaPanostusTeksti(self, kierros=2) -> int:

        if self.ai is not None: 
            valinta = self.ai.pyydaPanostus(kierros)

        else:
            if ((self.nakyma.maksettavaa is None) or (self.nakyma.pieniKorotus is None) or (self.nakyma.suuriKorotus is None) or (self.nakyma.panos is None)):
                raise ValueError("Panostuksesta puuttuu arvoja!")

            maksettavaa = self.nakyma.maksettavaa
            pieniKorotus = self.nakyma.pieniKorotus
            suuriKorotus = self.nakyma.suuriKorotus
            print("Maksettavaa:", maksettavaa, "|| Käsikortit:", self.nakyma.kasikortit, "|| Potti:", self.nakyma.potti)

            print("1. Check") if maksettavaa == 0 else print("1. Call, maksa:", min(maksettavaa, self.nakyma.chips))
            if (pieniKorotus > 0 and not any(p.valinta == 3 for p in self.nakyma.muutPelaajat)): 
                print("2. Pieni korotus:", pieniKorotus + maksettavaa, "| korotuksen osuus:", pieniKorotus)
            if (suuriKorotus > 0 and suuriKorotus > pieniKorotus):
                print("3. Suuri korotus:", suuriKorotus + maksettavaa, "| korotuksen osuus:", suuriKorotus)
            print("4. Fold, menetät pottiin maksetut:", self.nakyma.maksettuJakoon)

            try:
                valinta = int(input("Valintasi: "))
                if valinta not in (1,2,3,4):
                    valinta = 1
            except ValueError:
                valinta = 1

        return int(valinta) 
        


class PelaajaNakyma:
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
     

class MuutNakee:
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



        