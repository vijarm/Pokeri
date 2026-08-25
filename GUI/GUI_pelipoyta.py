import pygame
from . import settings
from random import randint



# ============================================================
# ASETUKSET
# ============================================================

WIDTH = settings.WIDTH
HEIGHT = settings.HEIGHT

SIDE_WIDTH = 190
TOP_BAR_HEIGHT = 52

CENTER_LEFT = SIDE_WIDTH
CENTER_RIGHT = WIDTH - SIDE_WIDTH
CENTER_WIDTH = CENTER_RIGHT - CENTER_LEFT

DECK_X = 785
DECK_Y = 320


#Korttien kuvien x,y sijainti sheetissä
MAA_RIVIT = {
    "PATA": 0,
    "RISTI": 1,
    "HERTTA": 2,
    "RUUTU": 3,
    "muu": 4
}

NUMERO_SARAKKEET = {
    14: 0,
    2: 1,
    3: 2,
    4: 3,
    5: 4,
    6: 5,
    7: 6,
    8: 7,
    9: 8,
    10: 9,
    11: 10,
    12: 11,
    13: 12
}


CARD_WIDTH = 78
CARD_HEIGHT = 108
CARD_GAP = 8

CARD_COUNT = 5

CARDS_WIDTH = (
    CARD_COUNT * CARD_WIDTH
    + (CARD_COUNT - 1) * CARD_GAP
)

PLAYER_PANEL_WIDTH = 145
PLAYER_PANEL_HEIGHT = 105

PLAYER_GROUP_WIDTH = (
    PLAYER_PANEL_WIDTH
    + 25
    + CARDS_WIDTH
)

PLAYER_GROUP_LEFT = (
    CENTER_LEFT
    + (CENTER_WIDTH - PLAYER_GROUP_WIDTH) // 2
)



# ============================================================
# VÄRIT
# ============================================================

TABLE_GREEN = settings.TABLE_GREEN
TABLE_DARK = settings.TABLE_DARK

PANEL_COLOR = settings.PANEL_COLOR
PANEL_DARK = settings.PANEL_DARK

WHITE = settings.WHITE
BLACK = settings.BLACK
GRAY = settings.GRAY
LIGHT_GRAY = settings.LIGHT_GRAY

RED = settings.RED
BLUE = settings.BLUE
LIGHT_BLUE = settings.LIGHT_BLUE
GOLD = settings.GOLD
TURKOOSI = settings.TURKOOSI
ORANSSI = settings.ORANSSI

small_font = settings.small_font
font = settings.font
medium_font = settings.medium_font
large_font = settings.large_font
title_font = settings.title_font



class GUI_pelipoyta:

    def __init__(self, screen, nakyma, kortit_sheet):
        self.screen = screen
        self.kortit_sheet = kortit_sheet
        self.nakyma = nakyma
        self.valintapaneeli = ValintaPaneeli(nakyma, kortit_sheet)
        self.animaatiot = []

    def handle_event(self, event):
        self.valintapaneeli.handle_event(event)

    def asetaNakyma(self, uusinakyma):
        self.nakyma = uusinakyma
        self.valintapaneeli.nakyma = uusinakyma

    def handle_tapahtuma(self, tapahtuma):
        if tapahtuma["tapahtuma"] == "fold_voitto":
            self.valintapaneeli.mode = "fold_voitto"

        if tapahtuma["tapahtuma"] == "jaaKortit":
            self.valintapaneeli.mode = "odottaa"
            self.jaaKortit()

        if tapahtuma["tapahtuma"] == "panostus":

            #self.valintapaneeli.mode = "odottaa"  Sitten kun toimii seuraavat stepit samalla logiikalla
            if tapahtuma["valinta"] == 4:  #fold
                self.foldaa(tapahtuma["pelaaja"])
            else:
                self.ilmoita(tapahtuma["pelaaja"], tapahtuma["ilmoitus"])

        if tapahtuma["tapahtuma"] == "pyydaPanos":
            if tapahtuma["pelaaja"] == self.nakyma.nimi:
                self.valintapaneeli.mode = "panostus"
            else:
                self.valintapaneeli.mode = "odottaa"

        if tapahtuma["tapahtuma"] == "ilmoitus":
            #self.valintapaneeli.mode = "odottaa"   Sitten kun toimii seuraavat stepit samalla logiikalla
            self.ilmoita(tapahtuma["pelaaja"], tapahtuma["ilmoitus"])


                                       
    def draw(self):
        
        pygame.display.set_caption(
            "POKERISIMULAATTORI"
        )

        self.screen.fill(TABLE_DARK)

        self.draw_top_bar()

        self.draw_bottom_player()

        self.draw_side_player("left")

        self.draw_top_player()

        self.draw_side_player("right")

        self.draw_center_area()

        self.valintapaneeli.draw(self.screen) #Valintapaneelin oma sisältö muuttuu pelitilanteen mukaan

        for animaatio in self.animaatiot:
            animaatio.draw()


    def get_kortin_paikka(self, pelaaja, index):  #palauttaa ((sijainti x, sijainti y), rotaatio)

        if pelaaja == self.nakyma:  #oma pelaaja
            start_x = (PLAYER_GROUP_LEFT + PLAYER_PANEL_WIDTH + 25)
            x = (start_x + index * (CARD_WIDTH + CARD_GAP) + CARD_WIDTH // 2)
            y = 658
            return ((x, y), 0)

        elif pelaaja == self.nakyma.muutPelaajat[0]:
            x = (SIDE_WIDTH // 2)
            y = (230 + index * 80)
            return ((x, y), 90)

        elif pelaaja == self.nakyma.muutPelaajat[1]:
            start_x = (PLAYER_GROUP_LEFT + PLAYER_PANEL_WIDTH + 25)
            x = (start_x + index * (CARD_WIDTH + CARD_GAP) + CARD_WIDTH // 2)
            y = 121
            return ((x, y), 0)

        elif pelaaja == self.nakyma.muutPelaajat[2]:
            x = (WIDTH - SIDE_WIDTH // 2)
            y = (230 + index * 80)
            return ((x, y), 270)

        else:
            raise ValueError("Virheellinen pelaajavalinta")


    def draw_top_player(self):
        surface = self.screen
        pelaaja = self.nakyma.muutPelaajat[1]
        kortit_sheet = self.kortit_sheet

        panel_x = PLAYER_GROUP_LEFT

        #Pelaajapaneeli
        panel_rect = pygame.Rect(panel_x, 68, PLAYER_PANEL_WIDTH, PLAYER_PANEL_HEIGHT)

        draw_player_panel(surface, pelaaja, panel_rect)

        # Kortit
        if pelaaja.aktiivinen and not pelaaja.folded and not pelaaja.kasikortit == None:
            kortit = pelaaja.kasikortit
            for i, card in enumerate(kortit):

                sijainti, rotation = self.get_kortin_paikka(pelaaja, i)

                draw_card(surface, card, sijainti, CARD_WIDTH, CARD_HEIGHT, kortit_sheet)


    def draw_side_player(self, side):

        surface = self.screen
        if side == "left":
            pelaaja = self.nakyma.muutPelaajat[0]
        else:
            pelaaja = self.nakyma.muutPelaajat[2]

        kortit_sheet = self.kortit_sheet

        if side == "left":
            panel_x = 15

        else:
            panel_x = (WIDTH - SIDE_WIDTH + 15)

        #Pelaajapaneeli
        panel_rect = pygame.Rect(panel_x, 75, 160, 105)

        draw_player_panel(surface, pelaaja, panel_rect)

        #Kortit
        if pelaaja.aktiivinen and not pelaaja.folded and not pelaaja.kasikortit == None:
            kortit = pelaaja.kasikortit
            for i, card in enumerate(
                kortit   
            ):
                sijainti, rotation = self.get_kortin_paikka(pelaaja, i)

                draw_card(surface, card, sijainti, CARD_WIDTH, CARD_HEIGHT, kortit_sheet, rotation=rotation)

    def draw_bottom_player(self):  #Oma pelaaja

        surface = self.screen
        pelaaja = self.nakyma
        valintapaneeli = self.valintapaneeli
        kortit_sheet = self.kortit_sheet

        #Pelaajapaneeli
        panel_x = PLAYER_GROUP_LEFT

        panel_rect = pygame.Rect(panel_x, 605, PLAYER_PANEL_WIDTH, PLAYER_PANEL_HEIGHT)

        draw_player_panel(surface, pelaaja, panel_rect)

        #Kortit
        if pelaaja.aktiivinen:
            for i, kortti in enumerate(pelaaja.kasikortit):

                selected = i in valintapaneeli.valitutKortit

                sijainti, rotation = self.get_kortin_paikka(pelaaja, i)

                if selected:  # Nostetaan valittuja kortteja
                    sijainti = (sijainti[0], sijainti[1] - 10)

                rect = draw_card(surface, kortti, sijainti, CARD_WIDTH, CARD_HEIGHT, kortit_sheet, selected=selected)

                valintapaneeli.kortti_rectit[i] = rect

    #Keskialue, logi ym muut lisätietoikkunat
    def draw_center_area(self):
        surface = self.screen
        nakyma = self.nakyma
        kortit_sheet = self.kortit_sheet

        #Logi, noin 5 riviä tekstiä (lisää? scroll bar?)
        log_height = 105
        log_bottom = 712

        log_rect = pygame.Rect(15, log_bottom - log_height, 270, log_height)

        draw_panel(surface, log_rect)

        messages = nakyma.log[-5:]  # 5 uusinta merkintää näkyy

        y = log_rect.y + 10

        for message in reversed(messages):

            draw_text(surface, message, (log_rect.x + 10, y), small_font)
            y += 18

        #Potti info
        pot_x = 620
        pot_y = 300

        draw_centered_text(surface, "POTTI", (pot_x, pot_y), medium_font)

        draw_centered_text(surface, nakyma.potti, (pot_x, pot_y + 38), large_font, GOLD)

        draw_centered_text(surface,
            f"Suurin korotus: {nakyma.suurinKorotus}",
            (pot_x, pot_y + 72), small_font, GRAY)

        #Pakka
        deck_x = DECK_X
        deck_y = DECK_Y

        for offset in [8, 4, 0]:

            draw_card(surface, "alaspain", (deck_x + offset, deck_y + offset), 78, 108, kortit_sheet)

        draw_centered_text(surface,
            "PAKKA",
            (deck_x, deck_y + 72), small_font)
    
    #Yläpalkki, vähemmän relevanttia infoa
    def draw_top_bar(self):
        surface = self.screen
        nakyma = self.nakyma

        pygame.draw.rect(surface, PANEL_DARK, (0, 0, WIDTH, TOP_BAR_HEIGHT) )

        draw_text(surface,
            "MARKKAPOKERI",
            (18, 13), title_font)

        draw_text(surface,
            f"Jako {nakyma.kierros}",
            (400, 17) )

        draw_text(surface,
            f"Pelivaihe: {PELIVAIHE[nakyma.pelivaihe]}",
            (515, 17) )

        draw_text(surface,
            f"Jakaja: {nakyma.jakaja}",
            (790, 17) )


    #Animaatiofunktiot

    def jaaKortit(self):
        jakoAnimaatio = Korttijako(self)
        jakoAnimaatio.aloitaJako()
        self.animaatiot.append(jakoAnimaatio)


    def foldaa(self, pelaaja):
        foldAnimaatio = FoldAnimaatio(self, pelaaja)
        foldAnimaatio.aloita()
        self.animaatiot.append(foldAnimaatio)
        self.animaatiot.append(Ilmoitus(self, self.haePelaajanPaikka(pelaaja), "FOLDAAN"))

    def ilmoita(self, pelaaja, teksti):
        self.animaatiot.append(Ilmoitus(self, self.haePelaajanPaikka(pelaaja), teksti))

        
    def haePelaajanPaikka(self, pelaaja):  #Hakee nimen perusteella pelaajan paikan (0 = bottom, 1 = left, 2 = top, 3 = right)
        pelaajat = [self.nakyma] + self.nakyma.muutPelaajat
        pelaajaIndex = pelaajat.index(next(p for p in pelaajat if p.nimi == pelaaja))
        return pelaajaIndex

                        

        



# Piirtämisen apufunktiot

def draw_text(surface, text, position, font_object=font, color=WHITE):

    rendered = font_object.render(str(text), True, color)
    surface.blit(rendered, position)


def draw_centered_text(surface, text, center, font_object=font, color=WHITE):

    rendered = font_object.render(str(text), True, color)
    rect = rendered.get_rect(center=center)
    surface.blit(rendered, rect)


def draw_panel(surface, rect, border_color=LIGHT_GRAY, border_width=2):

    pygame.draw.rect(surface, PANEL_COLOR, rect, border_radius=8)

    pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=8)


#Pelaajapaneeli

def draw_player_panel(surface, pelaaja, rect):

    if pelaaja.allin:
        border_color = TURKOOSI
    elif not pelaaja.aktiivinen:
        border_color = GRAY
    elif pelaaja.folded:
        border_color = LIGHT_GRAY
    elif pelaaja.valinta == 2 or pelaaja.valinta == 3:
        border_color = RED
    else:
        border_color = GOLD

    if pelaaja.folded:
        tila = "Luovuttanut"
    elif pelaaja.allin:
        tila ="All-in"
    else:
        tila = VALINNAT[pelaaja.valinta]

    draw_panel(surface, rect, border_color, border_width = 3)

    draw_text(surface, pelaaja.nimi, (rect.x + 10, rect.y + 8), medium_font)

    draw_text(surface, f"Chips: {pelaaja.chips}", (rect.x + 10, rect.y + 31), medium_font)

    if pelaaja.aktiivinen:

        draw_text(surface,
            f"Potissa: {pelaaja.maksettuJakoon}",
            (rect.x + 10, rect.y + 57), small_font)

        draw_text(surface,
            tila,  
            (rect.x + 10, rect.y + 77), small_font)

    else: 

        draw_text(surface,
            "Tippunut pelistä",
            (rect.x + 10, rect.y + 57), small_font)

    if pelaaja.aktiivinen:  #TÄHÄN SE VUOROSSA TÄGI, tai kokonaan veks

        draw_text(surface,
            "● VUOROSSA",
            (rect.x + 10, rect.bottom - 20), small_font, GOLD)


# ============================================================
# KORTTI
# ============================================================

def create_card_surface(kortti, width, height, kortit_sheet, selected=False):
    kortin_kuva = get_kortin_kuva(kortti, kortit_sheet)
    
    card_surface = pygame.Surface( (width, height), pygame.SRCALPHA)

    card_surface.blit(kortin_kuva, (0, 0))  # Piirretään kortin kuva

    # Pyöristetään kortin kulmat läpinäkyvällä
    mask = pygame.Surface( (width, height), pygame.SRCALPHA)  

    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, width, height), border_radius=7)

    card_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    border_color = (ORANSSI if selected
        else BLACK)

    border_width = (4 if selected
        else 2)

    pygame.draw.rect(card_surface, border_color, (0, 0, width, height), width=border_width, border_radius=7)
    
    return card_surface


def draw_card(surface, kortti, center, width, height, kortit_sheet, rotation=0, selected=False):
    card_surface = create_card_surface(kortti, width, height, kortit_sheet, selected)

    if rotation != 0:
        card_surface = pygame.transform.rotate(card_surface, rotation)

    rect = card_surface.get_rect(center=center)

    surface.blit(card_surface, rect)

    return rect


def get_kortin_kuva(kortti, kortit_sheet, tausta=2):  

    if kortti == "alaspain" or kortti.alaspain == True:  #Väärinpäin olevat kortit
        y = MAA_RIVIT["muu"] * CARD_HEIGHT
        x = NUMERO_SARAKKEET[tausta] * CARD_WIDTH
    else:
        y = MAA_RIVIT[kortti.maa] * CARD_HEIGHT
        x = NUMERO_SARAKKEET[kortti.numero] * CARD_WIDTH

    rect = pygame.Rect(
        x,
        y,
        CARD_WIDTH,
        CARD_HEIGHT
    )

    return kortit_sheet.subsurface(rect)




# ============================================================
# VALINTAPANEELI, TÄSSÄ TAPAHTUU PELAAJAN VALINNAT
# ============================================================

class ValintaPaneeli:

    def __init__(self, nakyma, kortit_sheet):

        # "panostus"
        # "vaihdot"
        # "showdown"
        # "..."

        self.left = 390
        self.top = 465
        self.width = 500
        self.height = 120
        
        self.nakyma = nakyma
        self.mode = "panostus"
        self.kortit_sheet = kortit_sheet

        self.valinta: str | None = None

        self.vaihdettavat: list | None = None
        self.valitutKortit = []
        self.kortti_rectit = {}

        self.jatketaan = None

        self.panostus_buttons = {
            "maksa": pygame.Rect(402, 540, 110, 35),
            "pieniKorotus": pygame.Rect(524, 540, 110, 35),
            "suuriKorotus": pygame.Rect(646, 540, 110, 35),
            "luovuta": pygame.Rect(768, 540, 110, 35),
        }

        self.vaihtoNappi_rect = pygame.Rect(585, 540, 110, 35)  #Yhdistetään napit, yksi OK??

        self.jatkaNappi_rect = pygame.Rect(585, 540, 110, 35)


    def handle_event(self, event):

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if self.mode == "odottaa":
            return

        elif self.mode == "panostus":

            for valinta, rect in self.panostus_buttons.items():

                if rect.collidepoint(event.pos):
                    if self.valintaSallittu(valinta):
                        self.valinta = valinta
                    print("PANOSTUSVALINTA:", valinta)

        elif self.mode == "vaihdot":

            if event.type == pygame.MOUSEBUTTONDOWN:

                for i, rect in self.kortti_rectit.items():

                    if rect.collidepoint(event.pos):

                        if i in self.valitutKortit:
                            self.valitutKortit.remove(i)
                        else:
                            self.valitutKortit.append(i)
                        return

                if self.vaihtoNappi_rect.collidepoint(event.pos):
                    self.vaihdettavat = self.valitutKortit.copy()

        elif self.mode == "showdown":

            if event.type == pygame.MOUSEBUTTONDOWN:

                if self.jatkaNappi_rect.collidepoint(event.pos):
                    self.jatketaan = True

        elif self.mode == "fold_voitto":

            if event.type == pygame.MOUSEBUTTONDOWN:

                if self.jatkaNappi_rect.collidepoint(event.pos):
                    self.jatketaan = True


    def get_valinta(self):  # TÄHÄN SISÄÄN voi laittaa sen, että kun vastaus hyväksytään niin siirtyy mode "odottaa". EN saanu aiemmin toimimaan?

        if self.mode == "panostus":

            valinta = self.valinta
            self.valinta = None
            return valinta

        if self.mode == "vaihdot":

            if self.vaihdettavat is None:
                return None
            
            vaihdettavat = self.vaihdettavat.copy()
            self.vaihdettavat = None
            self.valitutKortit = []
            return vaihdettavat

        if self.mode == "showdown":

            jatketaan = self.jatketaan
            self.jatketaan = None

            if jatketaan is not None:
                self.mode = "odottaa"

            return jatketaan

        if self.mode == "fold_voitto":

            jatketaan = self.jatketaan
            self.jatketaan = None

            if jatketaan is not None:
                self.mode = "odottaa"
            return jatketaan

                
    def draw(self, surface):

        rect = pygame.Rect(self.left, self.top, self.width, self.height)

        draw_panel(surface, rect, GOLD)

        if self.mode == "odottaa": 

            draw_centered_text(surface,
                "Pelaaja 2:n vuoro",  # vuorossa?
                (rect.centerx, rect.y + 25), medium_font)

            draw_centered_text(surface, 
                "Odotetaan...",   
                (rect.centerx, rect.y + 25), medium_font, GRAY)

        elif self.mode == "panostus":

            draw_centered_text(surface,
                f"Maksettavaa: {self.nakyma.maksettavaa}",
                (rect.centerx, rect.y + 30), medium_font)

            draw_centered_text(surface,
                f"Minimikorotus: {self.nakyma.panos}",
                (rect.centerx, rect.y + 50), medium_font)


            for valinta, rect in self.panostus_buttons.items():  #Napit

                if self.valintaSallittu(valinta):  #Tarkistaa onko valinta mahdollinen
                    color = GOLD
                    text_color = BLACK

                else:
                    color = GRAY
                    text_color = LIGHT_GRAY

                pygame.draw.rect(surface, color, rect)

                draw_centered_text(surface, self.valintaTeksti(valinta), rect.center, font, text_color)

        elif self.mode == "vaihdot":

            draw_centered_text(surface,
                "VALITSE VAIHDETTAVAT KORTIT",
                (rect.centerx, rect.y + 30), large_font)

            pygame.draw.rect(surface, GOLD, self.vaihtoNappi_rect)

            draw_centered_text(surface,
                "VAIHDA",
                self.vaihtoNappi_rect.center, font, BLACK)

        elif self.mode == "showdown":

            draw_centered_text(surface, 
                "KÄSIEN VERTAILU", 
                (rect.centerx, rect.y + 30), large_font)

            pygame.draw.rect(surface, GOLD, self.jatkaNappi_rect)

            draw_centered_text(surface, "JATKA", self.jatkaNappi_rect.center, font, BLACK)

            if self.nakyma.showdown is not None:
                self.piirraShowdown(surface)

        elif self.mode == "fold_voitto":

            voittaja = self.nakyma.showdown

            draw_centered_text(surface,
                "MUUT PELAAJAT LUOVUTTIVAT",
                (rect.centerx, rect.y + 30), medium_font)

            draw_centered_text(surface,
                f"{voittaja["voittaja"].nimi} voitti {voittaja["potti"]} markkaa!",
                (rect.centerx, rect.y + 50), medium_font)

            pygame.draw.rect(surface, GOLD, self.jatkaNappi_rect)

            draw_centered_text(surface, "JATKA", self.jatkaNappi_rect.center, font, BLACK)


    def valintaSallittu(self, valinta):  #Lopullisessa versiossa noita None tsekkejä ei pitäisi tarvita
        nakyma = self.nakyma

        if nakyma.maksettavaa is not None and nakyma.pieniKorotus is not None and nakyma.suuriKorotus is not None:
            if valinta == "maksa":  #Maksaminen on aina mahdollinen jos pelaajaa on kutsuttu panostuskierrokselle
                return True

            if valinta == "pieniKorotus":
                if (nakyma.pieniKorotus > 0 and not any(p.valinta == 3 for p in nakyma.muutPelaajat)):
                    return True
                else:
                    return False

            if valinta == "suuriKorotus":
                if (nakyma.suuriKorotus > 0 and nakyma.suuriKorotus > nakyma.pieniKorotus):
                    return True
                else:
                    return False

            if valinta == "luovuta":
                if nakyma.maksettavaa > 0:
                    return True
                else:
                    return False

    def valintaTeksti(self, valinta):
        nakyma = self.nakyma
        if nakyma.maksettavaa is not None and nakyma.pieniKorotus is not None and nakyma.suuriKorotus is not None:
            if valinta == "maksa":
                if nakyma.maksettavaa == 0:
                    return "Check!"
                else:
                    return f"Maksa {nakyma.maksettavaa}"

            if valinta == "pieniKorotus":
                return f"Korota {nakyma.pieniKorotus + nakyma.maksettavaa}"
            
            if valinta == "suuriKorotus":
                return f"Korota {nakyma.suuriKorotus + nakyma.maksettavaa}"

            if valinta == "luovuta":
                return "Luovuta"

    def piirraShowdown(self, surface):

        rect = pygame.Rect(CENTER_LEFT + 80, TOP_BAR_HEIGHT + 150, CENTER_WIDTH - 160, 250)
        
        draw_panel(surface, rect, GOLD)

        showdown = self.nakyma.showdown

        kortit = showdown["kasikortit"]
        kasi = showdown["kasinimi"]
        voittaja = showdown["voittaja"]
        voittopotti = showdown["potti"]
        pottiajaljella = showdown["pottiaJaljella"]

        draw_text(surface,
            f"Voittaja: {voittaja}, voittokäsi: {kasi}",
            (rect.x + 20, rect.y + 20), medium_font, WHITE)

        draw_text(surface,
            f"Voittopotti: {voittopotti} merkkiä",
            (rect.x + 20, rect.y + 50),
             medium_font, WHITE)

        if pottiajaljella > 0:  #Jos jaettiin vasta sidepot ja loppupotin jakaminen jatkuu
            draw_text(surface,
                f"Pottiin jäi vielä jaettavaksi {pottiajaljella} merkkiä",
                (rect.x + 20, rect.y + 80), medium_font, WHITE)

        for i, kortti in enumerate(kortit):  #Voittokäden piirtäminen

            kokonaisleveys = 5 * CARD_WIDTH + 4 * (CARD_GAP + 6) 
            x = (rect.centerx - kokonaisleveys // 2 + i * (CARD_WIDTH + CARD_GAP + 6) + CARD_WIDTH // 2)
            y = (self.top - 90)

            draw_card(surface, kortti, (x, y), CARD_WIDTH, CARD_HEIGHT, self.kortit_sheet)


# Kortin liikkumisen animaatio
class KorttiAnimaatio:

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
                    sijainti, rotaatio = self.pelipoytaGUI.get_kortin_paikka(pelaaja, kierros)

                    animaatio = KorttiAnimaatio("alaspain", (DECK_X, DECK_Y), sijainti, 0.3, rotaatio, viive)
                    self.animaatiot.append(animaatio)
                viive += 0.1

    def paivita(self, dt):
        for animaatio in self.animaatiot:
            animaatio.paivita(dt)
            if all(animaatio.valmis for animaatio in self.animaatiot):
                self.valmis = True

    def draw(self):
        for animaatio in self.animaatiot:
            draw_card(self.pelipoytaGUI.screen, animaatio.kortti, animaatio.sijainti, CARD_WIDTH, CARD_HEIGHT, self.pelipoytaGUI.kortit_sheet, rotation=animaatio.rotation)


class FoldAnimaatio:
    def __init__(self, pelipoytaGUI, pelaaja):
        self.pelipoytaGUI = pelipoytaGUI
        self.animaatiot = []
        self.valmis = False
        self.aika = 0

        pelaajat = [pelipoytaGUI.nakyma] + pelipoytaGUI.nakyma.muutPelaajat
        self.foldaaja = next(p for p in pelaajat if p.nimi == pelaaja)

    def aloita(self):
        
        for i in range(len(self.foldaaja.kasikortit)):
            loppusijainti = (randint(SIDE_WIDTH + 200, WIDTH - (SIDE_WIDTH + 200)), randint(HEIGHT - 500, HEIGHT - 200))
            loppurotaatio = randint(-400, 400)
            kesto = randint(20, 40) / 100

            alkusijainti, alkurotaatio = self.pelipoytaGUI.get_kortin_paikka(self.foldaaja, i)
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

    
class Ilmoitus:

    def __init__(self, pelipoytaGUI, pelaaja, ilmoitus):  #pelaaja lähetetään valmiina indeksinä
        self.pelipoytaGUI = pelipoytaGUI
        self.valmis = False
        self.aika = 0
        self.ilmoitus = ilmoitus
        self.rect = pygame.Rect(ILMOITUSBOKSIT[pelaaja])
        self.tekstipaikka = ILMOITUSTEKSTIT[pelaaja]

    def paivita(self, dt):
        self.aika += dt
        if self.aika > 1.2:
            self.valmis = True
          
    def draw(self):
        #draw_panel(self.pelipoytaGUI.screen, self.rect)
        
        pygame.draw.rect(self.pelipoytaGUI.screen, (240, 130, 70), self.rect, border_radius=8)
        pygame.draw.rect(self.pelipoytaGUI.screen, BLACK, self.rect, width=2, border_radius=8)

        draw_text(self.pelipoytaGUI.screen, self.ilmoitus, self.tekstipaikka, large_font, BLACK)




        

VALINNAT = {
    0: "Odottaa",
    1: "Maksoi",
    2: "Pieni korotus",
    3: "Suuri korotus",
    4: "Luovutti"
}

PELIVAIHE = {
    0: "Odotetaan jakoa",
    1: "1. panostuskierros",
    2: "Vaihtokierros",
    3: "2. panostuskierros",
    4: "Käsien vertailu"
}

ILMOITUSBOKSIT = {
    0: (SIDE_WIDTH + 120, HEIGHT - 240, 210, 90),
    1: (SIDE_WIDTH, TOP_BAR_HEIGHT + 200, 210, 90),
    2: (SIDE_WIDTH + 200, 200, 210, 90),
    3: (SIDE_WIDTH + 690, TOP_BAR_HEIGHT + 220, 210, 90)
    }

ILMOITUSTEKSTIT = {
        0: (SIDE_WIDTH + 150, HEIGHT - 215),
        1: (SIDE_WIDTH + 30, TOP_BAR_HEIGHT + 235),
        2: (SIDE_WIDTH + 230, 235),
        3: (SIDE_WIDTH + 720, TOP_BAR_HEIGHT + 255)
    }
