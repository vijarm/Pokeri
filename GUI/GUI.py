import pygame
import sys
from . import settings

from .GUI_pelipoyta import GUI_pelipoyta
from .GUI_valikko import GUI_valikko

from viestit import Komento


WIDTH = settings.WIDTH
HEIGHT = settings.HEIGHT
FPS = settings.FPS

TABLE_GREEN = (27, 105, 66)
TABLE_DARK = (19, 77, 48)

WHITE = (245, 245, 245)
BLACK = (15, 15, 15)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)

small_font = settings.small_font
font = settings.font
medium_font = settings.medium_font
large_font = settings.large_font
title_font = settings.title_font

class GUI:
    def __init__(self, pelaaja, transport):
        pygame.init()
        self.transport = transport
        self.pelaaja = pelaaja
        self.nakyma = None
        self.mode = "valikko"

        self.paivitysjono = []  #Enginestä tulleet
        self.uusinPaivitys = None  

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        self.kortit_sheet = pygame.image.load("assets/kortit.png").convert_alpha()

        self.GUI_valikko = GUI_valikko(self.screen, self.pelaaja, self.kortit_sheet, self.lisaaKomento)
        self.GUI_pelipoyta = GUI_pelipoyta(self.screen, self.nakyma, self.kortit_sheet, self.lisaaKomento)

        self.clock = pygame.time.Clock()

    def process_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.mode == "valikko":
                self.GUI_valikko.handle_event(event)

            elif self.mode == "pelipoyta":
                self.GUI_pelipoyta.handle_event(event)


    def draw(self):

        if self.mode == "valikko":
            self.GUI_valikko.draw()

        elif self.mode == "pelipoyta":
            self.GUI_pelipoyta.draw()

        pygame.display.flip()

    def paivita(self, dt):  #Hakee enginen tuottamat pelitilannemuutokset ja uudet pelinäkymät

        paivitykset = self.transport.receive_for_gui()

        #for p in paivitykset:
            #print("TRANSPORTISTA TULI:", p.tyyppi, p.tiedot)

        self.paivitysjono.extend(paivitykset)

        for paivitys in self.paivitysjono:
            if paivitys.tyyppi == "vaihda_gui_mode":
                self.mode = paivitys.tiedot["uusi_mode"]
                self.paivitysjono.remove(paivitys)

                if self.mode == "valikko":
                    self.GUI_pelipoyta.resetoi()

                break

            elif paivitys.tyyppi == "host_disconnect" or paivitys.tyyppi == "host_perui":
                self.mode = "valikko"
                self.lisaaKomento("host_disconnect", self.pelaaja.nimi, {}, oma_engine=True)
                self.GUI_pelipoyta.resetoi()
                self.GUI_valikko.handle_paivitys(paivitys)

        if self.paivitysjono and not self.GUI_pelipoyta.animaatiot:  #Jonossa tehtäviä ja animaatio ei käynnissä, otetaan uusi
            self.uusinPaivitys = self.paivitysjono.pop(0)
            #print("OTETTIIN KÄSITTELYYN:", self.uusinPaivitys.tyyppi)

            if self.uusinPaivitys.tyyppi == "aloita_peli":

                self.GUI_pelipoyta.resetoi()
                self.GUI_valikko.liityOnline.resetoi()
                self.GUI_valikko.mode = "main"
                self.asetaNakyma(self.uusinPaivitys.uusinakyma)
                self.mode = self.uusinPaivitys.tiedot["uusi_mode"]
                self.uusinPaivitys = None

            elif self.mode == "valikko":
                self.GUI_valikko.handle_paivitys(self.uusinPaivitys)
                self.uusinPaivitys = None

            elif self.uusinPaivitys.tyyppi == "pelipoyta":
                self.GUI_pelipoyta.handle_tapahtuma(self.uusinPaivitys.tiedot)


        if self.mode == "valikko":

            self.GUI_valikko.paivita()
            self.GUI_pelipoyta.animaatiot.clear()

            
        if self.mode == "pelipoyta":

            if self.GUI_pelipoyta.animaatiot:
                for animaatio in self.GUI_pelipoyta.animaatiot:
                    animaatio.paivita(dt)
                self.GUI_pelipoyta.animaatiot = [a for a in self.GUI_pelipoyta.animaatiot if not a.valmis]

            if self.uusinPaivitys is not None and not self.GUI_pelipoyta.animaatiot:
                self.asetaNakyma(self.uusinPaivitys.uusinakyma)
                self.uusinPaivitys = None


            
    def lisaaKomento(self, tapahtuma, pelaaja, tiedot={}, oma_engine=False):
        komento = Komento(tapahtuma, pelaaja, tiedot)

        if tapahtuma == "poistu_pelipoydasta" or tapahtuma == "peli_ohi": #Tapahtuu välittömästi käymättä enginen kautta
            self.mode = "valikko"

        if oma_engine:
            self.transport.send_to_own_engine(komento)

        else: 
            self.transport.send_to_engine(komento)  #Normaalisti käytetään tätä, mutta parissa kohtaa clientin täytyy ohittaa

    


    def asetaNakyma(self, uusinakyma):
        self.nakyma = uusinakyma
        self.GUI_pelipoyta.asetaNakyma(uusinakyma)

