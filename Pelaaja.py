from AI.AI import randomAI, montecarloAI, steadycarloAI, superAI
from Pistelasku import laskeArvot

AI_TYYPIT = {
    "random": randomAI,
    "montecarlo": montecarloAI,
    "steady": steadycarloAI,
    "vahvistusoppinut": superAI
}

class Pelaaja:
    def __init__(self, nimi, tyyppi, AI_valinta=None):
        self.nimi: str = nimi
        self.tyyppi: str = tyyppi
        self.aktiivinen: bool = True

        self.nakyma: PelaajaNakyma

        if AI_valinta is not None:
            self.ai = AI_TYYPIT[AI_valinta](self)
        else:
            self.ai = None

        self.kasikortit: list = []
        self.chips: int = 1000
        self.allin: bool = False
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
        self.maksettuJakoon = 0
        self.vaihtoja = None

    def nollaaPanos(self):
        self.maksettuPanostukseen = 0
        self.valinta = 0

    def tulostaKasi(self):
        print(f"Pelaaja {self.nimi}, käsikortit: {self.kasikortit}")

    def pyydaVaihdot(self) -> list:
        vaihdettavat = []
        if self.ai is not None:
            vaihdettavat = self.ai.vaihdaKortit()
        else:  # Nää tulee myöhemmin GUI:n kautta
            analysoitu = laskeArvot(self.nakyma.kasikortit, vaihtoja=True)
            vaihdetaanIndex = input("Mitä vaihdetaan indeksillä?")
            if vaihdetaanIndex.strip() == "": return []

            if vaihdetaanIndex.strip() == "a":  #Ota suositus
                if len(analysoitu["vaihtosuositus"]) > 0:
                    for kortti in analysoitu["vaihtosuositus"][0]:
                        vaihdettavat.append(kortti)

            else:
                lista = vaihdetaanIndex.split(" ")  #Ota indexit syötteestä
                for i in lista:
                    vaihdettavat.append(self.nakyma.kasikortit[int(i)])

        return vaihdettavat

    def pyydaPanostus(self) -> int:

        #Tähän joku kutsu jos on AI
        if self.ai is not None: 
            #valinta = self.ai.pyydaPanostus()
            return 1

        else:
            maksettavaa = self.nakyma.suurinKorotus - self.nakyma.maksettuPanostukseen
            print("Maksettavaa:", maksettavaa, "|| Käsikortit:", self.nakyma.kasikortit, "|| Potti:", self.nakyma.potti)
            print("1. Check") if maksettavaa == 0 else print("1. Call")
            if (self.nakyma.chips > maksettavaa): print("2. Raise") 
            print("3. Fold")

            try:
                valinta = int(input("Valintasi: "))
                if valinta not in (1,2,3):
                    valinta = 1
            except ValueError:
                valinta = 1

            return int(valinta)
        





class PelaajaNakyma:
    def __init__(self, pelaaja, pelipoyta):

        self.nimi = pelaaja.nimi
        self.aktiivinen = pelaaja.aktiivinen

        self.kasikortit = pelaaja.kasikortit
        self.chips = pelaaja.chips
        self.allin = pelaaja.allin
        self.maksettuJakoon = pelaaja.maksettuJakoon
        self.maksettuPanostukseen = pelaaja.maksettuPanostukseen
        self.valinta = pelaaja.valinta  # 1 call, 2 raise, 3 fold
        self.vaihtoja = pelaaja.vaihtoja

        self.pelivaihe = pelipoyta.pelivaihe  # 1 = 1. panostus | 2 = vaihdot | 3 = 2. panostus | 4 = showdown
        self.kierros = pelipoyta.kierros
        self.jakaja = pelipoyta.jakaja.nimi

        if pelipoyta.jako is not None:
            self.potti = pelipoyta.jako.potti
            self.mukanaPotissa = [p.nimi for p in pelipoyta.jako.mukanaPotissa]  #Ei pelaajaolioita viewiin, vain nimiä
            self.panos = pelipoyta.jako.alkupanos

            if pelipoyta.jako.panostuskierros is not None:
                self.pelaajaVuorossa = pelipoyta.jako.panostuskierros.pelaajaVuorossa.nimi
                self.suurinKorotus = pelipoyta.jako.panostuskierros.suurinKorotus 

        self.muutPelaajat = []

        for toinen in pelipoyta.pelaajat:
            if toinen != pelaaja:
                self.muutPelaajat.append(MuutNakee(toinen))
     

class MuutNakee:
    def __init__(self, pelaaja):
        self.nimi = pelaaja.nimi
        self.tyyppi = pelaaja.tyyppi
        self.aktiivinen = pelaaja.aktiivinen
        self.chips = pelaaja.chips
        self.allin = pelaaja.allin
        self.maksettuJakoon = pelaaja.maksettuJakoon
        self.maksettuPanostukseen = pelaaja.maksettuPanostukseen
        self.valinta = pelaaja.valinta
        self.vaihtoja = pelaaja.vaihtoja
        