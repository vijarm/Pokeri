import random

Maat = ["PATA", "HERTTA", "RISTI", "RUUTU"]

class Pakka:
    def __init__(self):
        self.kortit=[]
    
    def luo_pakka(self):
        for maa in Maat:
            for i in range(2, 15):
                self.kortit.append(Kortti(maa, i))

    def sekoita(self):
        random.shuffle(self.kortit)
          
    def nosta(self) -> Kortti:
        return self.kortit.pop()
    
    def nosta_x(self, maara: int) -> list:
        nostetut_kortit = []
        for _ in range(maara):
            nostetut_kortit.append(self.kortit.pop())
        return nostetut_kortit
    
    def jaaKortit(self, pelaajia: int, kortteja: int) -> list:
        kadet = [[] for _ in range(pelaajia)]
        for _ in range(kortteja):
            for i in range(pelaajia):
                kadet[i].append(self.kortit.pop())
        return kadet
    

class Kortti:
    def __init__(self, maa, numero, alaspain=False):
        self.maa: str = maa
        self.numero: int = numero
        self.alaspain: bool = alaspain

    
    def __str__(self):
        return f"{self.maa} {self.numero}"

    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return (
            isinstance(other, Kortti)
            and self.maa == other.maa
            and self.numero == other.numero
        )

    def to_dict(self):
        return {
            "maa": self.maa,
            "numero": self.numero,
            "alaspain": self.alaspain
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            maa=data["maa"],
            numero=data["numero"],
            alaspain=data.get("alaspain", False)
        )

    def toString(self):
        print(self.maa, self.numero)

    def nollaa(self):
        self.alaspain = False



    




