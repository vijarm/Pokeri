import pygame
from . import settings
from .piirtofunktiot import draw_card, draw_centered_text, draw_panel, draw_player_panel, draw_text
from random import sample
from Pakka import Pakka
import pyperclip

WIDTH = settings.WIDTH
HEIGHT = settings.HEIGHT

CARD_WIDTH = 78
CARD_HEIGHT = 108

TABLE_GREEN = settings.TABLE_GREEN
TABLE_DARK = settings.TABLE_DARK

WHITE = settings.WHITE
BLACK = settings.BLACK
GRAY = settings.GRAY
LIGHT_GRAY = settings.LIGHT_GRAY

RED = settings.RED
LIGHT_RED = settings.LIGHT_RED
BLUE = settings.BLUE
LIGHT_BLUE = settings.LIGHT_BLUE
GOLD = settings.GOLD
TURKOOSI = settings.TURKOOSI
ORANSSI = settings.ORANSSI

font = settings.font
medium_font = settings.medium_font
large_font = settings.large_font
title_font = settings.title_font
very_large_font = settings.very_large_font
jatti_font = settings.jatti_font


class GUI_valikko:

    def __init__(self, screen, pelaaja, kortit_sheet, lisaaKomento):
        self.screen = screen
        self.kortit_sheet = kortit_sheet
        self.lisaaKomento = lisaaKomento
        self.oma_pelaaja = pelaaja
        self.pelaajat = [pelaaja, None, None, None]
        self.simulointiPelaajat = [None, None, None, None]
        self.pelipoyta = None
        self.muokkaus_popup = None
        self.liityOnline = LiityOnline(self)
        

        self.mainNapit = []
        for i, tiedot in enumerate(MAIN_NAPIT):
            self.mainNapit.append(Nappi(500, 270+(i*80), 280, 60, tiedot[0], tiedot[1], LIGHT_GRAY, font=large_font))

        self.pelaajavalintaNapit = [ [], [], [], [] ]
        for i in range(4):
            self.pelaajavalintaNapit[i].append(Nappi(WIDTH-430, 145+(i*115), 100, 50, "lisaa", "LISÄÄ", LIGHT_BLUE, BLACK))
            self.pelaajavalintaNapit[i].append(Nappi(WIDTH-430, 145+(i*115), 100, 50, "muokkaa", "MUOKKAA", GOLD, BLACK))
            self.pelaajavalintaNapit[i].append(Nappi(WIDTH-315, 145+(i*115), 100, 50, "poista", "POISTA", RED, BLACK))

        self.pelaajavalintaMuut = []
        self.pelaajavalintaMuut.append(Nappi(WIDTH//2 - 160, HEIGHT - 140, 140, 60, "aloita_peli", "ALOITA", GOLD, BLACK, BLACK, large_font))
        self.pelaajavalintaMuut.append(Nappi(WIDTH//2 + 20, HEIGHT - 140, 140, 60, "palaa_menuun", "PERUUTA", GRAY, BLACK, BLACK, large_font))

        self.mode = "main"

        pakka = Pakka()
        pakka.luo_pakka()
        self.viuhka1 = sample(pakka.kortit, 5).copy()
        self.viuhka2 = sample(pakka.kortit, 5).copy()


    def handle_paivitys(self, paivitys):
        if paivitys.tyyppi == "uusipelaaja":
            if self.mode == "simuloi":
                self.simulointiPelaajat[paivitys.tiedot["indeksi"]] = paivitys.tiedot["pelaaja"]

            else:
                self.pelaajat[paivitys.tiedot["indeksi"]] = paivitys.tiedot["pelaaja"]
            return



    def handle_event(self, event):

        if self.muokkaus_popup:
            self.muokkaus_popup.handle_event(event)
            if self.muokkaus_popup.suljetaan:
                self.muokkaus_popup = None
            return


        if self.mode == "main":

            if event.type != pygame.MOUSEBUTTONDOWN:
                return

            for nappi in self.mainNapit:
                if nappi.clicked(event.pos):
                    print("CLIKCATTU", nappi.nimi)
                    self.handle_nappi(nappi.nimi)


        elif self.mode == "pelaajavalinta":

            if event.type == pygame.MOUSEBUTTONDOWN:

                for nappi in self.pelaajavalintaMuut:
                    if nappi.clicked(event.pos):
                        print("CLICKATTU", nappi.nimi)
                        self.handle_nappi(nappi.nimi)

                for pelaajaindeksi, napit in enumerate(self.pelaajavalintaNapit):
                    for nappi in napit:
                        if nappi.clicked(event.pos):
                            print("CLICKATTU", nappi.nimi)
                            self.handle_nappi(nappi.nimi, pelaajaindeksi)


        elif self.mode == "liity":

            self.liityOnline.handle_event(event)


        elif self.mode == "simuloi":

            if event.type == pygame.MOUSEBUTTONDOWN:

                for nappi in self.pelaajavalintaMuut:
                    if nappi.clicked(event.pos):
                        print("CLICKATTU", nappi.nimi)
                        self.handle_nappi(nappi.nimi)

                for pelaajaindeksi, napit in enumerate(self.pelaajavalintaNapit):
                    for nappi in napit:
                        if nappi.clicked(event.pos):
                            print("CLICKATTU", nappi.nimi)
                            self.handle_nappi(nappi.nimi, pelaajaindeksi)


    def handle_nappi(self, valinta, pelaajaindeksi=None):

        if self.mode == "main":
            if valinta == "poistu":
                self.lisaaKomento("sulje_peli", self.oma_pelaaja)
                return

            elif valinta == "pelaajavalinta":
                self.mode = "pelaajavalinta"

            elif valinta == "liity":
                self.mode = "liity"

            elif valinta == "simuloi":
                self.mode = "simuloi"

        elif self.mode == "pelaajavalinta":

            if valinta == "aloita_peli":
                if sum(p is not None for p in self.pelaajat) < 2:
                    self.muokkaus_popup = IlmoitusPopup(self.screen, "Tarvitaan vähintään 2 pelaajaa!")
                    return

                self.lisaaKomento("aloita_peli", self.pelaajat)
                self.mode = "main"

            elif valinta == "palaa_menuun":
                self.mode = "main"

            elif valinta == "lisaa":
                assert pelaajaindeksi is not None
                self.muokkaus_popup = Muokkaus_popup(self, self.pelaajat[pelaajaindeksi], pelaajaindeksi)

            elif valinta == "muokkaa":
                assert pelaajaindeksi is not None
                self.muokkaus_popup = Muokkaus_popup(self, self.pelaajat[pelaajaindeksi], pelaajaindeksi)

            elif valinta == "poista":
                assert pelaajaindeksi is not None
                self.pelaajat[pelaajaindeksi] = None
                return

        elif self.mode == "simuloi":
            if valinta == "aloita_peli":
                if sum(p is not None for p in self.simulointiPelaajat) < 2:
                    self.muokkaus_popup = IlmoitusPopup(self.screen, "Tarvitaan vähintään 2 pelaajaa!")
                    return

                self.lisaaKomento("aloita_peli", self.simulointiPelaajat)  #Tietty eri moodilla sit jatkossa
                self.mode = "main"

            elif valinta == "palaa_menuun":
                self.mode = "main"

            elif valinta == "lisaa":
                assert pelaajaindeksi is not None
                self.muokkaus_popup = Muokkaus_popup(self, self.simulointiPelaajat[pelaajaindeksi], pelaajaindeksi, simulointi = True)

            elif valinta == "muokkaa":
                assert pelaajaindeksi is not None
                self.muokkaus_popup = Muokkaus_popup(self, self.simulointiPelaajat[pelaajaindeksi], pelaajaindeksi, simulointi = True)

            elif valinta == "poista":
                assert pelaajaindeksi is not None
                self.simulointiPelaajat[pelaajaindeksi] = None
                return



    def get_valinta(self):
        pass

    def paivita(self):
        if self.mode == "pelaajavalinta" or self.mode == "simuloi":
            self.paivitaPelaajaNapit()
    
    
    def draw(self): 
        
        pygame.display.set_caption(
            "POKERISIMULAATTORI"
        )

        self.screen.fill(TABLE_DARK)

        if self.mode == "main":        
            draw_main_menu(self)

        elif self.mode == "pelaajavalinta":
            draw_pelaajavalinta(self)

        elif self.mode == "liity":
            self.liityOnline.draw()

        elif self.mode == "simuloi":
            draw_pelaajavalinta(self, simulointi=True)


    def paivitaPelaajaNapit(self):
        pelaajat = self.pelaajat if self.mode != "simuloi" else self.simulointiPelaajat

        for i, napit in enumerate(self.pelaajavalintaNapit):
            if pelaajat[i] is None:
                napit[0].enabled = True  #lisää
                napit[1].enabled = False  #muokkaa
                napit[2].enabled = False  #poista

            elif pelaajat[i] == self.oma_pelaaja:
                napit[0].enabled = False
                napit[1].enabled = True
                napit[2].enabled = False

            else:
                napit[0].enabled = False
                napit[1].enabled = True
                napit[2].enabled = True




def draw_main_menu(gui_valikko):
    screen = gui_valikko.screen
    draw_centered_text(screen, "POKERISIMULAATTORI", (640, 130), jatti_font, BLACK)

    for nappi in gui_valikko.mainNapit:
        nappi.draw(gui_valikko.screen)

    draw_korttiviuhka(gui_valikko, gui_valikko. viuhka1, 250, 350)
    draw_korttiviuhka(gui_valikko, gui_valikko. viuhka2, WIDTH - 250, 350)



def draw_pelaajavalinta(gui_valikko, simulointi=False):
    screen = gui_valikko.screen
    pelaajat = gui_valikko.pelaajat if simulointi == False else gui_valikko.simulointiPelaajat

    draw_centered_text(screen, "PELAAJAT", (WIDTH // 2, 60), pygame.font.SysFont("arial black", 48), BLACK)

    for i in range(4): 
        draw_panel(screen, (200, 120 + i*115, WIDTH - 400, 100))  #taustat

        pelaaja = pelaajat[i]
        if pelaaja is not None:
            tyyppiteksti = ""
            if pelaaja == gui_valikko.oma_pelaaja:
                tyyppiteksti = "Oma pelaajasi"
            elif pelaaja.ai is None:
                tyyppiteksti = pelaaja.tyyppi
            else:
                tyyppiteksti = f"AI, {pelaaja.ai.luokka}, {next(key for key, val in AGGR_VAIHTOEHDOT.items() if val == pelaaja.ai.aggressiivisuus)}"
            
            draw_text(screen, f"{pelaaja.nimi}", (220, 160 + i*115), large_font, GOLD)
            draw_text(screen, tyyppiteksti, (450, 160 + i*115), large_font, GOLD)
            gui_valikko.pelaajavalintaNapit[i][1].draw(screen)  #muokkaa
            gui_valikko.pelaajavalintaNapit[i][2].draw(screen)  #poista
        else:
            draw_text(screen, ("Vapaa pelipaikka"), (230, 160 + i*115), large_font, GOLD)
            gui_valikko.pelaajavalintaNapit[i][0].draw(screen)  #lisää

    for nappi in gui_valikko.pelaajavalintaMuut:
        nappi.draw(screen)

    if gui_valikko.muokkaus_popup:
        gui_valikko.muokkaus_popup.draw()


def draw_korttiviuhka(gui_valikko, kortit, x, y):
    screen = gui_valikko.screen
    draw_card(screen, kortit[0], (x - 60, y), CARD_WIDTH, CARD_HEIGHT, gui_valikko.kortit_sheet, 40)
    draw_card(screen, kortit[1], (x - 30, y - 25), CARD_WIDTH, CARD_HEIGHT, gui_valikko.kortit_sheet, 20)
    draw_card(screen, kortit[2], (x - 0, y - 35), CARD_WIDTH, CARD_HEIGHT, gui_valikko.kortit_sheet, 0)
    draw_card(screen, kortit[3], (x + 30, y - 25), CARD_WIDTH, CARD_HEIGHT, gui_valikko.kortit_sheet, -20)
    draw_card(screen, kortit[4], (x + 60, y), CARD_WIDTH, CARD_HEIGHT, gui_valikko.kortit_sheet, -40)


class LiityOnline:
    def __init__(self, gui_valikko):
        self.screen = gui_valikko.screen
        self.gui_valikko = gui_valikko
        self.nimi = arvoNimi()
        self.lisaaKomento = gui_valikko.lisaaKomento
        self.popup = None

        self.ip = ""
        self.connected = False

        self.napit = []
        self.napit.append(Nappi(WIDTH//2 - 160, HEIGHT - 140, 140, 60, "liity_peliin", "LIITY", GOLD, BLACK, BLACK, large_font))
        self.napit.append(Nappi(WIDTH//2 + 20, HEIGHT - 140, 140, 60, "palaa_menuun", "PERUUTA", GRAY, BLACK, BLACK, large_font))

        self.nimiboksi = Tekstiboksi( (WIDTH // 2 - 110, 260, 260, 45), self.nimi)
        self.ipboksi = Tekstiboksi( (WIDTH // 2 - 110, 430, 260, 45), "anna_ip", max_length=30)

    def draw(self):
        screen = self.screen

        draw_centered_text(screen, "LIITY NETTIPELIIN", (WIDTH // 2, 60), pygame.font.SysFont("arial black", 48), BLACK)

        draw_panel(screen, (WIDTH // 2 - 300, 180, 600, 150))
        draw_centered_text(screen, "Pelaajan nimi:", (WIDTH // 2, 225), large_font, WHITE)
        self.nimiboksi.draw(screen)

        draw_panel(screen, (WIDTH // 2 - 300, 350, 600, 150))
        draw_centered_text(screen, "IP-osoite:", (WIDTH // 2, 395), large_font, WHITE)
        self.ipboksi.draw(screen)

        for nappi in self.napit:
            nappi.draw(self.screen)

        if self.popup:
            self.popup.draw()

    def handle_event(self, event):

        if self.popup:
            self.popup.handle_event(event)
            if self.popup.suljetaan == True:
                self.popup = None            
            return

        if event.type == pygame.KEYDOWN and self.nimiboksi.active:
            self.nimiboksi.handle_event(event)
            return

        if event.type == pygame.KEYDOWN and self.ipboksi.active:
            self.ipboksi.handle_event(event)
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.nimiboksi.active = self.nimiboksi.rect.collidepoint(event.pos) #Tekstiboksi aktiivinen tai epäaktiivinen onko klikattu vai ei
            self.ipboksi.active = self.ipboksi.rect.collidepoint(event.pos)

        for nappi in self.napit:
            if event.type == pygame.MOUSEBUTTONDOWN:

                if nappi.clicked(event.pos):
                    print("CLIKCATTU", nappi.nimi)
                    self.handle_nappi(nappi.nimi)
                    return

    def handle_nappi(self, nappi):
        if nappi == "palaa_menuun":
            self.gui_valikko.mode = "main"

        if nappi == "liity_peliin":  # Ei luoda itse pelaaja-oliota vaan lähetetään hostille nimi
            if len(self.nimiboksi.get()) < 3:
                self.popup = IlmoitusPopup(self.screen, "Nimeen tarvitaan vähintään 3 merkkiä!")
                return

            if len(self.ipboksi.get()) < 8:
                self.popup = IlmoitusPopup(self.screen, "Tarkista ip-osoite!")
                return

            self.popup = IlmoitusPopup(self.screen, "Yhdistetään!", TABLE_GREEN)




class Nappi:
    def __init__(self, x, y, leveys, korkeus, nimi, teksti, vari, kehys=None, tekstivari=BLACK, font=medium_font):
        self.rect = pygame.Rect(x, y, leveys, korkeus)
        self.nimi = nimi
        self.teksti = teksti
        self.vari = vari
        self.kehys = kehys
        self.tekstivari = tekstivari
        self.font = font
        self.enabled = True

    def draw(self, screen):
        if self.enabled:
            pygame.draw.rect(screen, self.vari, self.rect, border_radius = 4)
            if self.kehys is not None:
                pygame.draw.rect(screen, self.kehys, self.rect, 3, border_radius = 4) 

            draw_centered_text(screen, self.teksti, self.rect.center, self.font, self.tekstivari)

    def clicked(self, pos):
        if not self.enabled:
            return False
        
        return self.rect.collidepoint(pos)

class Tekstiboksi:
    def __init__(self, rect, teksti="", max_length=16):
        self.rect = pygame.Rect(rect)
        self.teksti = teksti
        self.active = False
        self.max_length = max_length

    def handle_event(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.teksti = self.teksti[:-1]

        elif event.key == pygame.K_RETURN:
            self.active = False

        elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.teksti += pyperclip.paste()

        else:
            if len(self.teksti) <= self.max_length:
                self.teksti += event.unicode

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, RED if self.active else BLACK, self.rect, 3)
        text_surface = large_font.render(self.teksti, True, BLACK)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 8))

        if self.active:
            cursor_x = self.rect.x + 10 + text_surface.get_width()
            pygame.draw.line(
                screen,
                BLACK,
                (cursor_x, self.rect.y + 6),
                (cursor_x, self.rect.bottom - 9),
                2
            )

    def get(self):
        return self.teksti


class Muokkaus_popup:
    def __init__(self, gui_valikko, pelaaja, indeksi, simulointi = False):
        self.screen = gui_valikko.screen
        self.pelaajat = gui_valikko.pelaajat if simulointi == False else gui_valikko.simulointiPelaajat
        self.muokattava = pelaaja
        self.indeksi = indeksi
        self.lisaaKomento = gui_valikko.lisaaKomento
        self.suljetaan = False

        #Muokattavat arvot
        self.nimi = ""
        self.tyyppi = ""
        self.oma_pelaaja = False
        self.ai = None
        self.ai_aggressiivisuus = None
        self.ai_strategia = None

        self.popup = None

        if pelaaja == gui_valikko.oma_pelaaja:
            self.oma_pelaaja = True
            self.nimi = pelaaja.nimi
            self.tyyppi = pelaaja.tyyppi


        elif pelaaja is not None:
            self.nimi = pelaaja.nimi
            self.tyyppi = pelaaja.tyyppi
            if pelaaja.ai is not None:
                self.ai = pelaaja.ai.luokka
                self.ai_aggressiivisuus = pelaaja.ai.aggressiivisuus
                self.ai_strategia = pelaaja.ai.strategia

        else:
            self.nimi = arvoNimi()
            self.tyyppi = "Tietsikka"
            self.ai = "Monte Carlo"
            self.ai_aggressiivisuus = 2
            self.ai_strategia = None


        #Boksit, napit ym piirtotietoja
        self.rect = pygame.Rect(400, 100, WIDTH-800, HEIGHT-200)  #tausta
        self.napit = []
        self.napit.append(Nappi(self.rect.centerx - 120, HEIGHT - 170, 100, 50, "tallenna", "TALLENNA", LIGHT_BLUE, BLACK, BLACK, medium_font))
        self.napit.append(Nappi(self.rect.centerx + 20, HEIGHT - 170, 100, 50, "sulje_popup", "PERUUTA", RED, BLACK, BLACK, medium_font))
        self.nimiboksi = Tekstiboksi( (self.rect.centerx-120, 170, 240, 40), self.nimi)
        self.ai_valinta = RullaavaValinta(AI_VAIHTOEHDOT, (self.rect.centerx - 180, 385, 360, 50))
        self.aggr_valinta = RullaavaValinta(list(AGGR_VAIHTOEHDOT.keys()), (self.rect.centerx - 180, 495, 360, 50))

    def draw(self):

        #pop-up tausta
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.rect, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, self.rect, width=3, border_radius=8)

        draw_centered_text(self.screen, "NIMI:", (self.rect.centerx, 150), large_font, BLACK)
        self.nimiboksi.draw(self.screen)

        #draw_centered_text(self.screen, f"{self.nimi}", (self.rect.centerx, 190), large_font, BLACK)

        draw_centered_text(self.screen, "TYYPPI:", (self.rect.centerx, 260), large_font, BLACK)
        draw_centered_text(self.screen, "Oma pelaajasi" if self.oma_pelaaja else f"{self.tyyppi}", (self.rect.centerx, 300), large_font, BLACK)
       
        if self.ai:
            draw_centered_text(self.screen, "AI-LUOKKA:", (self.rect.centerx, 370), large_font, BLACK)
            #draw_centered_text(self.screen, f"{self.ai}", (self.rect.centerx, 410), large_font, BLACK)
            self.ai_valinta.draw(self.screen)

            draw_centered_text(self.screen, "AGGRESSIIVISUUS:", (self.rect.centerx, 480), large_font, BLACK)
            #draw_centered_text(self.screen, f"{self.ai_aggressiivisuus}", (self.rect.centerx, 520), large_font, BLACK)
            self.aggr_valinta.draw(self.screen)

        for nappi in self.napit:
            nappi.draw(self.screen)

        if self.popup:
            self.popup.draw()

    def handle_event(self, event):

        if self.popup:
            self.popup.handle_event(event)
            if self.popup.suljetaan == True:
                self.popup = None            
            return

        if event.type == pygame.KEYDOWN and self.nimiboksi.active:
            self.nimiboksi.handle_event(event)
            return

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.nimiboksi.active = self.nimiboksi.rect.collidepoint(event.pos) #Tekstiboksi aktiivinen tai epäaktiivinen onko klikattu vai ei

        for nappi in self.napit:
            if nappi.clicked(event.pos):
                print("CLIKCATTU", nappi.nimi)
                self.handle_nappi(nappi.nimi)
                return

        self.ai_valinta.handle_event(event)
        self.aggr_valinta.handle_event(event)
            

    def handle_nappi(self, valinta):
        if valinta == "sulje_popup":
            self.suljetaan = True

        elif valinta == "tallenna":
            nimi = self.nimiboksi.teksti

            for pelaaja in self.pelaajat:  #Ei tuplanimiä
                if pelaaja is None or pelaaja == self.muokattava:
                    continue
                else:
                    if pelaaja.nimi == nimi:
                        self.popup = IlmoitusPopup(self.screen, "NIMI ON JO VARATTU")
                        return
                    elif len(nimi) < 2:
                        self.popup = IlmoitusPopup(self.screen, "NIMEEN TARVITAAN VÄHINTÄÄN 3 MERKKIÄ")
                        return

            tiedot = {"nimi": nimi, 
                "tyyppi": self.tyyppi, 
                "ai": self.ai_valinta.get(), 
                "ai_aggressiivisuus": AGGR_VAIHTOEHDOT[self.aggr_valinta.get()], 
                "ai_strategia": self.ai_strategia,
                "indeksi": self.indeksi}

            if self.muokattava == None:
                self.lisaaKomento("luo_pelaaja", self.muokattava, tiedot)
                self.suljetaan = True
                return

            if self.oma_pelaaja:  #Jos nimeä on muokattu lähetetään tieto
                if nimi != self.muokattava.nimi:
                    self.lisaaKomento("muokkaa_pelaajaa", self.muokattava, tiedot)
                self.suljetaan = True  
                return

            else:
                self.lisaaKomento("muokkaa_pelaajaa", self.muokattava, tiedot)
                self.suljetaan = True
                return



class IlmoitusPopup:
    def __init__(self, screen, teksti, vari=RED):
        self.screen = screen
        self.teksti = teksti
        self.vari = vari
        self.suljetaan = False
        self.rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 120, 400, 200)
        self.nappi = Nappi(self.rect.x + 100, self.rect.y + 115, 200, 60, "ok", "OK", GRAY, BLACK, BLACK, large_font)

    def draw(self):

        #pop-up tausta
        pygame.draw.rect(self.screen, self.vari, self.rect, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, self.rect, width=3, border_radius=8)
        draw_centered_text(self.screen, self.teksti, (self.rect.centerx, self.rect.y + 60), large_font, BLACK)
        self.nappi.draw(self.screen)

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        if self.nappi.clicked(event.pos):
            self.suljetaan = True


class RullaavaValinta:

    def __init__(self, vaihtoehdot, rect, font=large_font):
        self.vaihtoehdot = vaihtoehdot
        self.valittu = 0
        self.rect = pygame.Rect(rect)
        self.font = font

        self.button_width = 50

        self.left_button = pygame.Rect(self.rect.left, self.rect.top, self.button_width, self.rect.height)

        self.right_button = pygame.Rect(self.rect.right - self.button_width, self.rect.top, self.button_width, self.rect.height)


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:

            if self.left_button.collidepoint(event.pos):
                self.valittu = (self.valittu - 1) % len(self.vaihtoehdot)

            elif self.right_button.collidepoint(event.pos):
                self.valittu = (self.valittu + 1) % len(self.vaihtoehdot)

    def get(self):
        return self.vaihtoehdot[self.valittu]

    def draw(self, screen):

        # Tausta
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 3, border_radius=8)

        # Nuolet
        pygame.draw.rect(screen, GOLD, self.left_button, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.left_button, 3, border_radius=8)

        pygame.draw.rect(screen, GOLD, self.right_button, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.right_button, 3, border_radius=8)

        # Vasen nuoli <
        left_text = self.font.render("<", True, BLACK)
        left_pos = left_text.get_rect(center=self.left_button.center)
        screen.blit(left_text, left_pos)

        # Oikea nuoli >
        right_text = self.font.render(">", True, BLACK)
        right_pos = right_text.get_rect(center=self.right_button.center)
        screen.blit(right_text, right_pos)

        # Nykyinen valinta
        text = self.font.render(str(self.get()), True, BLACK)
        text_pos = text.get_rect(center=self.rect.center)
        screen.blit(text, text_pos)



def arvoNimi():
    etuosa = sample(etunimet, 1)
    takaosa = sample(takanimet, 1)
    return f"{etuosa[0]}-{takaosa[0]}"



MAIN_NAPIT = [
    ("pelaajavalinta", "ALOITA UUSI PELI"), 
    ("liity", "LIITY NETTIPELIIN"),
    ("simuloi", "SIMULOI PELEJÄ"),
    ("asetukset", "ASETUKSET"),
    ("poistu", "POISTU")
    ]

AI_VAIHTOEHDOT = ["Monte Carlo", "Satunnainen", "Koneoppinut"]
AGGR_VAIHTOEHDOT = {"Normaali": 2, "Aggressiivinen": 3, "Maltillinen": 1}

etunimet = [
    "Pokeri", "Jokeri", "Jätkä", "Ässä", "Hertta",
    "Ruutu", "Risti", "Pata", "Bluffi", "Sökö",
    "Hullu", "Kuningas", "Seiska", "Jokeri", "Kortti",
    "Tuuri", "Kuuma", "Kylmä", "Hurja", "Villi",
    "Viekas", "Lucky", "Kuningatar", "Riski",
    "Röyhkeä", "Hämäys", "Täkäri", "Värisuora",
    "Luihu", "Urho", "Reilu", "Iso", "Pikku"
]

takanimet = [
    "Kalle", "Kari", "Kake", "Masa", "Make",
    "Jaska", "Jussi", "Pena", "Pete", "Reiska",
    "Rane", "Hai", "Haukka", "Susi", "Kettu",
    "Kobra", "Mursu", "Pomo", "Kunkku", "Ukko",
    "Varis", "Korppi", "Pöllö", "Noppa", "Piki",
    "Riepu", "Naksu", "Bingo", "Ruu", "Pimu",
    "Repe", "Boss", "Tiuku", "Akka", "Keke"
]