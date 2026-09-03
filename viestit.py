class Paivitys:
    def __init__(self, tyyppi, tiedot, uusinakyma=None):
        self.tyyppi = tyyppi
        self.tiedot = tiedot
        self.uusinakyma = uusinakyma

    def to_dict(self):
        return {
            "otsikko": "Paivitys",
            "tyyppi": self.tyyppi,
            "tiedot": self.tiedot,
            "uusinakyma": (self.uusinakyma.to_dict() if self.uusinakyma is not None else None)
        }

    @classmethod
    def from_dict(cls, data):
        from Pelaaja import PelaajaNakyma
        return cls(
            tyyppi=data["tyyppi"],
            tiedot=data["tiedot"],
            uusinakyma=(PelaajaNakyma.from_dict(data["uusinakyma"]) if data["uusinakyma"] is not None else None)
        )





class Komento:
    def __init__(self, tapahtuma, pelaaja, tiedot={}):
        self.tapahtuma = tapahtuma
        self.pelaaja = pelaaja
        self.tiedot = tiedot if tiedot is not None else {}

    def to_dict(self):
        return {
            "otsikko": "Komento",
            "tapahtuma": self.tapahtuma,
            "pelaaja": self.pelaaja,
            "tiedot": self.tiedot
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            tapahtuma=data["tapahtuma"],
            pelaaja=data["pelaaja"],
            tiedot=data["tiedot"]
        )