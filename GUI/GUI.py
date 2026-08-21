import pygame
import sys
from . import settings

from .GUI_pelipoyta import GUI_pelipoyta, ValintaPaneeli



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
    def __init__(self, pelaaja, pelipoyta):
        pygame.init()
        self.pelaaja = pelaaja
        self.pelipoyta = pelipoyta

        self.screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
        )

        self.current_screen = "GUI_pelipoyta"
        self.valintapaneeli = ValintaPaneeli(self.pelaaja)

        self.clock = pygame.time.Clock()

    def draw_snapshot(self):

        if self.current_screen == "GUI_pelipoyta":
            GUI_pelipoyta(self.screen, self.valintapaneeli, self.pelaaja.nakyma)

        pygame.display.flip()

    def run(self):
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

            self.valintapaneeli.handle_event(event)

    def draw(self):

        if self.current_screen == "GUI_pelipoyta":
            GUI_pelipoyta(
                self.screen,
                self.valintapaneeli,
                self.pelaaja.nakyma
            )

        pygame.display.flip()

