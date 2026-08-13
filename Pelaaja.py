
class Pelaaja:
    def __init__(self, nimi, tyyppi):
        self.nimi: str = nimi
        self.tyyppi: str = tyyppi
        self.aktiivinen: bool = True

        self.nakyma: PelaajaNakyma | None = None

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



class PelaajaNakyma:
    def __init__(self, pelaaja, pelipoyta):

        self.nimi = pelaaja.nimi
        self.aktiivinen = pelaaja.aktiivinen
        self.kasikortit = pelaaja.kasikortit
        self.chips = pelaaja.chips
        self.allin = pelaaja.allin
        self.maksettuJakoon = pelaaja.maksettuJakoon
        self.maksettuPanostukseen = pelaaja.maksettuPanostukseen
        self.valinta = pelaaja.valinta
        self.vaihtoja = pelaaja.vaihtoja

        if pelipoyta.jako is not None:
            self.pelivaihe = pelipoyta.jako.pelivaihe  # 1 = 1. panostus | 2 = vaihdot | 3 = 2. panostus | 4 = showdown
            self.potti = pelipoyta.jako.potti
            self.mukanaPotissa = [p.nimi for p in pelipoyta.jako.mukanaPotissa]  #Ei pelaajaolioita viewiin, vain nimiä
            self.panos = pelipoyta.jako.alkupanos
            self.suurinKorotus = pelipoyta.jako.suurinKorotus 
            self.vuoro = pelipoyta.jako.vuoro.nimi

        self.kierros = pelipoyta.kierros
        self.jakaja = pelipoyta.jakaja.nimi

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
        
