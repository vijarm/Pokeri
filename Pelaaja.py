class Pelaaja:
    def __init__(self, nimi, tyyppi):
        #yleiset
        self.nimi: str = nimi
        self.tyyppi: str = tyyppi

        self.aktiivinen: bool = True
        self.kasikortit: list = []
        self.chips: int = 1000
        self.allin: bool = False
        self.maksettuJakoon: int = 0
        self.maksettuPanostukseen: int = 0
        self.valinta: int = 0  # 1 = check/call, 2 = raise, 3 = fold
    
    def __str__(self):
        return f"{self.nimi}, {self.tyyppi}, stack: {self.chips}"

    def __repr__(self):
        return self.__str__()

    def toString(self):
        print(f"{self.nimi}, {self.tyyppi}, stack: {self.chips}")

    def nollaaKierros(self):
        self.kasikortit = []
        self.allin = False
        self.maksettuPottiin = 0

    def nollaaPanos(self):
        self.maksettuPanostukseen = 0
        self.valinta = 0
