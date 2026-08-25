import pygame
import sys
from . import settings

from .GUI_pelipoyta import GUI_pelipoyta



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
    def __init__(self, pelaaja, peli):
        pygame.init()
        self.peli = peli
        self.pelaaja = pelaaja
        self.pelipoyta = peli.pelipoyta
        self.nakyma = pelaaja.nakyma
        self.paivitysjono = []
        self.uusinPaivitys = None

        self.screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
        )

        self.kortit_sheet = pygame.image.load("assets/kortit.png").convert_alpha()

        self.GUI_pelipoyta = GUI_pelipoyta(self.screen, self.nakyma, self.kortit_sheet)

        self.current_screen = "GUI_pelipoyta"

        self.clock = pygame.time.Clock()

    def draw_snapshot(self):

        if self.current_screen == "GUI_pelipoyta":
            self.GUI_pelipoyta.draw()

        pygame.display.flip()

    def run(self):  #Tätähän ei nyt käytetä, kun se on tuolla MAIN loopissa? 
        running = True

        while running:

            self.process_events()
            self.pelipoyta.paivitaTila()
            self.draw()

            self.clock.tick(FPS)

                
        pygame.quit()
        sys.exit()

    def process_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            self.GUI_pelipoyta.handle_event(event)

    def draw(self):

        if self.current_screen == "GUI_pelipoyta":
            self.GUI_pelipoyta.draw()

        pygame.display.flip()

    def paivita(self, dt):  #Hakee enginen tuottamat pelitilannemuutokset ja uudet pelinäkymät
        paivitykset = self.pelipoyta.haePaivitykset()

        self.paivitysjono.extend(paivitykset)


        if self.paivitysjono and not self.GUI_pelipoyta.animaatiot:  #Jonossa tehtäviä ja animaatio ei käynnissä, otetaan uusi
            self.uusinPaivitys = self.paivitysjono.pop(0)

            if self.uusinPaivitys.kohde == "pelipoyta":
                self.GUI_pelipoyta.handle_tapahtuma(self.uusinPaivitys.tapahtuma)

            else:  #väliaikainen?
                self.asetaNakyma(self.uusinPaivitys.nakyma)
                self.uusinPaivitys = None


        if self.GUI_pelipoyta.animaatiot:
            for animaatio in self.GUI_pelipoyta.animaatiot:
                animaatio.paivita(dt)
            self.GUI_pelipoyta.animaatiot = [a for a in self.GUI_pelipoyta.animaatiot if not a.valmis]

        if self.uusinPaivitys is not None and not self.GUI_pelipoyta.animaatiot:
            self.asetaNakyma(self.uusinPaivitys.uusinakyma)
            self.uusinPaivitys = None
            

    def asetaNakyma(self, uusinakyma):
        self.nakyma = uusinakyma
        self.GUI_pelipoyta.asetaNakyma(uusinakyma)



