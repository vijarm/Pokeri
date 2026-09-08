class Paivitys:
    '''Paivitys -tyyppisenä viestinä engine lähettää tiedot uudesta pelitilanteesta GUI:lle.
    tyyppi: Pelitapahtuman tyyppi
    tiedot: Pelitapahtuman tarkemmat lisätiedot
    uusinakyma: Uuden pelitapahtuman jälkeen voimaan astuva näkymä (Pelaajanakyma -olio)
    '''

    def __init__(self, tyyppi, tiedot, uusinakyma=None):
        self.tyyppi = tyyppi
        self.tiedot = tiedot
        self.uusinakyma = uusinakyma

    def to_dict(self):
        '''Muuntaa Paivitys -olion tiedot dict-muotoon'''
        return {
            "otsikko": "Paivitys",
            "tyyppi": self.tyyppi,
            "tiedot": self.tiedot,
            "uusinakyma": (self.uusinakyma.to_dict() if self.uusinakyma is not None else None)
        }

    @classmethod
    def from_dict(cls, data):
        '''Muuntaa dict-muodossa olevan Paivityksen takaisin olioksi'''
        from Pelaaja import PelaajaNakyma
        return cls(
            tyyppi=data["tyyppi"],
            tiedot=data["tiedot"],
            uusinakyma=(PelaajaNakyma.from_dict(data["uusinakyma"]) if data["uusinakyma"] is not None else None)
        )


class Komento:
    '''Komento -tyyppisenä viestinä GUI lähettää tiedot GUI:ssa tehdyistä valinnoista pelin enginelle.
    tapahtuma: GUI:n tapahtuman tyyppi
    pelaaja: Pelaaja, jota komento pääasiallisesti koskee (valinnan tehnyt pelaaja, tai esimerkiksi menussa pelaaja, jota muutokset koskevat)
    tiedot: Mahdolliset tarkemmat komentoon liittyvät lisätiedot
    '''
    
    def __init__(self, tapahtuma, pelaaja, tiedot={}):
        self.tapahtuma = tapahtuma
        self.pelaaja = pelaaja
        self.tiedot = tiedot if tiedot is not None else {}

    def to_dict(self):
        '''Muuntaa Komento -olion tiedot dict-muotoon'''

        return {
            "otsikko": "Komento",
            "tapahtuma": self.tapahtuma,
            "pelaaja": self.pelaaja,
            "tiedot": self.tiedot
        }

    @classmethod
    def from_dict(cls, data):
        '''Muuntaa dict-muodossa olevan Komennon takaisin olioksi'''

        return cls(
            tapahtuma=data["tapahtuma"],
            pelaaja=data["pelaaja"],
            tiedot=data["tiedot"]
        )