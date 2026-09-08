import pygame
from . import settings
from random import randint
from .piirtofunktiot import draw_card, draw_centered_text, get_kortin_paikka

WIDTH = settings.WIDTH
HEIGHT = settings.HEIGHT

SIDE_WIDTH = 190
TOP_BAR_HEIGHT = 52

CENTER_LEFT = SIDE_WIDTH
CENTER_RIGHT = WIDTH - SIDE_WIDTH
CENTER_WIDTH = CENTER_RIGHT - CENTER_LEFT

DECK_X = 785
DECK_Y = 320

CARD_WIDTH = 78
CARD_HEIGHT = 108
CARD_GAP = 8

WHITE = settings.WHITE
BLACK = settings.BLACK
large_font = settings.large_font


class KorttiAnimaatio:
    '''Yleinen kortin liikuttamisen animaatio, jota käytetään apuna muiden animaatioiden toteuttamisessa'''

    def __init__(
        self,
        kortti,
        alku,
        loppu,
        kesto = 0.3,
        rotation = 0,
        viive = 0.0
    ):
        self.kortti = kortti
        self.sijainti = alku
        self.alku = alku
        self.loppu = loppu
        self.kesto = kesto
        self.rotationLoppu = rotation
        self.rotation = 0  #Aina alussa ovat pystysuorassa PAITSI EIVÄT jos lähtee sivupelaajalta

        self.viive = viive
        self.aika = 0
        self.valmis = False

    def paivita(self, dt):
        self.aika += dt

        if self.aika < self.viive:
            return
        
        t = min((self.aika - self.viive) / self.kesto, 1)
        x = (self.alku[0] + (self.loppu[0] - self.alku[0]) * t)
        y = (self.alku[1] + (self.loppu[1] - self.alku[1]) * t)
        self.sijainti = (x, y)
        self.rotation = self.rotationLoppu * t

        if t >= 1:
            self.valmis = True

class Korttijako:
    '''Animaatio, joka jakaa kortit kaikille pelaajille jaon alussa'''

    def __init__(self, pelipoytaGUI):
        self.pelipoytaGUI = pelipoytaGUI
        self.animaatiot = []
        self.valmis = False

        #Jakojärjestys sen mukaan, että alkaa jakajasta seuraavasta. Ei ehkä kuuluisi GUI:n puolelle.
        pelaajat = [pelipoytaGUI.nakyma] + pelipoytaGUI.nakyma.muutPelaajat
        jakajaIndex = pelaajat.index(next(p for p in pelaajat if p.nimi == pelipoytaGUI.nakyma.jakaja))
        jarjestys = pelaajat[jakajaIndex + 1 :] + pelaajat[ : jakajaIndex + 1]
        self.jaetaanPelaajille = [p for p in jarjestys if p.nimi in self.pelipoytaGUI.nakyma.mukanaPotissa]

    def aloitaJako(self):

        viive = 0  # Jotta kortit eivät lähde liikkeelle samaan aikaan
        
        for kierros in range(5):
            for pelaaja in self.jaetaanPelaajille:
                korttien_maara = 0
                if korttien_maara <= kierros:
                    sijainti, rotaatio = get_kortin_paikka(self.pelipoytaGUI, pelaaja, kierros)

                    animaatio = KorttiAnimaatio("alaspain", (DECK_X, DECK_Y), sijainti, 0.25, rotaatio, viive)
                    self.animaatiot.append(animaatio)
                viive += 0.075

    def paivita(self, dt):
        for animaatio in self.animaatiot:
            animaatio.paivita(dt)
            if all(animaatio.valmis for animaatio in self.animaatiot):
                self.valmis = True

    def draw(self):
        for animaatio in self.animaatiot:
            draw_card(self.pelipoytaGUI.screen, animaatio.kortti, animaatio.sijainti, CARD_WIDTH, CARD_HEIGHT, self.pelipoytaGUI.kortit_sheet, rotation=animaatio.rotation)


class FoldAnimaatio:
    '''Animaatio, jossa pelaaja heittää korttinsa pöydälle luovuttaessaan käden.'''

    def __init__(self, pelipoytaGUI, pelaaja):
        self.pelipoytaGUI = pelipoytaGUI
        self.animaatiot = []
        self.valmis = False
        self.aika = 0

        pelaajat = [pelipoytaGUI.nakyma] + pelipoytaGUI.nakyma.muutPelaajat
        self.foldaaja = next(p for p in pelaajat if p.nimi == pelaaja)

    def aloita(self):
        
        for i in range(len(self.foldaaja.kasikortit)):
            loppusijainti = (randint(SIDE_WIDTH + 200, WIDTH - (SIDE_WIDTH + 300)), randint(HEIGHT - 450, HEIGHT - 250))
            loppurotaatio = randint(-600, 600)
            kesto = randint(20, 40) / 100

            alkusijainti, alkurotaatio = get_kortin_paikka(self.pelipoytaGUI, self.foldaaja, i)
            animaatio = KorttiAnimaatio("alaspain", alkusijainti, loppusijainti, kesto, loppurotaatio)
            self.animaatiot.append(animaatio)

        self.foldaaja.kasikortit = [] #Jotta vanhat kortit standardipaikalla eivät näy

    def paivita(self, dt):
        self.aika += dt
        if self.aika > 1.4 and all(animaatio.valmis for animaatio in self.animaatiot):
            self.valmis = True
       
        for animaatio in self.animaatiot:
            animaatio.paivita(dt)
       
    def draw(self):
        for animaatio in self.animaatiot:
            draw_card(self.pelipoytaGUI.screen, animaatio.kortti, animaatio.sijainti, CARD_WIDTH, CARD_HEIGHT, self.pelipoytaGUI.kortit_sheet, rotation=animaatio.rotation)

    
class PelaajaIlmoitus:
    '''Staattinen ns. animaatio, jossa pelaaja ilmoittaa puhekuplalla pelitilanteen muutoksesta'''

    def __init__(self, pelipoytaGUI, pelaaja, ilmoitus):  #pelaaja lähetetään valmiina indeksinä
        self.pelipoytaGUI = pelipoytaGUI
        self.valmis = False
        self.aika = 0
        self.ilmoitus = ilmoitus
        self.pelaaja = pelaaja

    def paivita(self, dt):
        self.aika += dt
        if self.aika > 1.2:
            self.valmis = True
          
    def draw(self):

        puhekupla = pygame.Surface((210, 110), pygame.SRCALPHA)
        pygame.draw.ellipse(puhekupla, WHITE, (0, 0, 210, 90))  #pohja
        pygame.draw.polygon(puhekupla, (255, 255, 255), PUHEKUPLAT[self.pelaaja][1] )  #väkänen
        self.pelipoytaGUI.screen.blit(puhekupla, PUHEKUPLAT[self.pelaaja][0])
        
        draw_centered_text(self.pelipoytaGUI.screen, self.ilmoitus, PUHEKUPLAT[self.pelaaja][2], large_font, BLACK)

class OdotusAnimaatio:
    '''Ns. tyhjä animaatio, jolla voidaan luoda viivettä GUI:n muutoksiin, koska päivityksiä otetaan jonosta käsittelyyn vasta kun animaatiot ovat käsitelty loppuun'''

    def __init__(self, pelipoytaGUI, aika):
        self.aika = aika
        self.kulunutAika = 0
        self.valmis = False
        self.pelipoytaGUI = pelipoytaGUI

    def paivita(self, dt):
        self.kulunutAika += dt
        if self.kulunutAika >= self.aika:
            self.valmis = True
            self.pelipoytaGUI.valintapaneeli.mode = "odottaa"

    def draw(self):
        pass

class VaihtoAnimaatio:
    '''Animaatio korttien vaihdon yhteydessä, heittää vanhat kortit pois ja nostaa uudet kortit pakasta.'''

    def __init__(self, pelipoytaGUI, pelaaja, indeksit):
        self.pelipoytaGUI = pelipoytaGUI
        pelaajat = [pelipoytaGUI.nakyma] + pelipoytaGUI.nakyma.muutPelaajat
        self.pelaaja = next(p for p in pelaajat if p.nimi == pelaaja)
        self.vaihtoindeksit = indeksit

        self.animaatiot = []
        self.valmis = False
        self.aika = 0

    def aloita(self):  #PIIRTOON: if card is not None: normipiirrot jatkuu

        viive = 0  # Jotta kortit eivät lähde liikkeelle samaan aikaan
        tyhjatpaikat = []

        # Ensin vaihdettavat heitetään nurkkaan ja nykyiset käsikortit liikkuvat vasempaan reunaan
        for indeksi in range(5):  

            sijainti, rotaatio = get_kortin_paikka(self.pelipoytaGUI, self.pelaaja, indeksi)
            kohde = None

            if indeksi in self.vaihtoindeksit:  #Katsotaan mistä indekseistä kortit poistuvat, vaihdettavat heitetään ulos näytöltä
                tyhjatpaikat.append(indeksi)
                kohde = (WIDTH + 50, HEIGHT + 50)

            elif tyhjatpaikat:  #Vanhat kortit siirtyvät vasempaan laitaan tyhjille paikoille
                ekatyhja = tyhjatpaikat.pop(0)
                tyhjatpaikat.append(indeksi)
                kohde, kohderotaatio = get_kortin_paikka(self.pelipoytaGUI, self.pelaaja, ekatyhja)

            else:
                continue

            animaatio = KorttiAnimaatio(self.pelaaja.kasikortit[indeksi], sijainti, kohde, 0.3, rotaatio, viive)
            self.animaatiot.append(animaatio)

            self.pelaaja.kasikortit[indeksi] = None  #Alta paikka tyhjäksi, jotta vanhaa korttia ei piirretä
            viive += 0.1

        # Seuraavaksi pakasta jaetaan tyhjentyneille paikoille uudet kortit
        viive += 0.2
        for indeksi in tyhjatpaikat:
            kohde, rotaatio = get_kortin_paikka(self.pelipoytaGUI, self.pelaaja, indeksi)
            animaatio = KorttiAnimaatio("alaspain", (DECK_X, DECK_Y), kohde, 0.5, rotaatio, viive)
            self.animaatiot.append(animaatio)
            viive += 0.1

    def paivita(self, dt):
        self.aika += dt
        for animaatio in self.animaatiot:
            animaatio.paivita(dt)
        if all(animaatio.valmis for animaatio in self.animaatiot) and self.aika >= 1.5:
            self.valmis = True

    def draw(self):
        for animaatio in self.animaatiot:
            draw_card(self.pelipoytaGUI.screen, animaatio.kortti, animaatio.sijainti, CARD_WIDTH, CARD_HEIGHT, self.pelipoytaGUI.kortit_sheet, rotation=animaatio.rotation) 


PUHEKUPLAT = {  #[sijainti, väkänen pelaajan suuntaan, tekstipaikan sijainti] #(45,75), (25, 105), (65,85) vasen alas
    0: [(SIDE_WIDTH + 90, HEIGHT - 260), [(145,70), (185, 105), (185,75)], (SIDE_WIDTH + 195, HEIGHT - 215)],
    1: [(SIDE_WIDTH, TOP_BAR_HEIGHT + 200), [(25,20), (25,0), (65,20)], (SIDE_WIDTH + 105, TOP_BAR_HEIGHT + 245)],
    2: [(SIDE_WIDTH + 200, 200), [(25,20), (25,0), (65,20)], (SIDE_WIDTH + 305, 245)],
    3: [(SIDE_WIDTH + 690, TOP_BAR_HEIGHT + 160), [(145,20), (185,0), (185,20)], (SIDE_WIDTH + 795, TOP_BAR_HEIGHT + 205)]
    }

ILMOITUSTEKSTIT = {
        0: (SIDE_WIDTH + 150, HEIGHT - 215),
        1: (SIDE_WIDTH + 30, TOP_BAR_HEIGHT + 235),
        2: (SIDE_WIDTH + 230, 235),
        3: (SIDE_WIDTH + 720, TOP_BAR_HEIGHT + 255)
    }

