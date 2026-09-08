import pygame
from . import settings


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
very_large_font = settings.very_large_font
title_font = settings.title_font



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


# Pelipoydan perusrakenteen piirtäminen

def piirra_pelipoyta(gui_pelipoyta):
    '''Piirtää pelipöydän yleisnäkymän'''

    draw_top_bar(gui_pelipoyta)

    draw_bottom_player(gui_pelipoyta)

    draw_side_player(gui_pelipoyta, "left")

    if len(gui_pelipoyta.nakyma.muutPelaajat) > 1:
        draw_top_player(gui_pelipoyta)

    if len(gui_pelipoyta.nakyma.muutPelaajat) > 2:
        draw_side_player(gui_pelipoyta, "right")

    draw_center_area(gui_pelipoyta)


def get_kortin_paikka(gui_pelipoyta, pelaaja, index): 
    '''Hakee kortin sijainnin pelaajan ja käsikortin indeksin perusteella.
    Palauttaa sijainnin (x, y) sekä kortin rotaation'''

    nakyma = gui_pelipoyta.nakyma
    if pelaaja == nakyma:  #oma pelaaja
        start_x = (PLAYER_GROUP_LEFT + PLAYER_PANEL_WIDTH + 25)
        x = (start_x + index * (CARD_WIDTH + CARD_GAP) + CARD_WIDTH // 2)
        y = 658
        return ((x, y), 0)

    elif pelaaja == nakyma.muutPelaajat[0]:
        x = (SIDE_WIDTH // 2)
        y = (230 + index * 80)
        return ((x, y), 90)

    elif pelaaja == nakyma.muutPelaajat[1]:
        start_x = (PLAYER_GROUP_LEFT + PLAYER_PANEL_WIDTH + 25)
        x = (start_x + index * (CARD_WIDTH + CARD_GAP) + CARD_WIDTH // 2)
        y = 121
        return ((x, y), 0)

    elif pelaaja == nakyma.muutPelaajat[2]:
        x = (WIDTH - SIDE_WIDTH // 2)
        y = (230 + index * 80)
        return ((x, y), 270)

    else:
        raise ValueError("Virheellinen pelaajavalinta")


def draw_top_player(gui_pelipoyta):
    '''Piirtää ruudun ylälaidalla olevan pelaajan'''

    surface = gui_pelipoyta.screen
    pelaaja = gui_pelipoyta.nakyma.muutPelaajat[1]
    kortit_sheet = gui_pelipoyta.kortit_sheet

    panel_x = PLAYER_GROUP_LEFT

    #Pelaajapaneeli
    panel_rect = pygame.Rect(panel_x, 68, PLAYER_PANEL_WIDTH, PLAYER_PANEL_HEIGHT)

    draw_player_panel(surface, pelaaja, panel_rect)

    # Kortit
    if pelaaja.aktiivinen and not pelaaja.folded and not pelaaja.kasikortit == None:
        kortit = pelaaja.kasikortit
        for i, card in enumerate(kortit):

            sijainti, rotation = get_kortin_paikka(gui_pelipoyta, pelaaja, i)

            draw_card(surface, card, sijainti, CARD_WIDTH, CARD_HEIGHT, kortit_sheet)


def draw_side_player(gui_pelipoyta, side):
    '''Piirtää ruudun sivuilla olevat pelaajat.
    side: "left" = vasen, "right" = oikea '''

    surface = gui_pelipoyta.screen
    nakyma = gui_pelipoyta.nakyma

    if side == "left":
        pelaaja = nakyma.muutPelaajat[0]
    else:
        pelaaja = nakyma.muutPelaajat[2]

    kortit_sheet = gui_pelipoyta.kortit_sheet

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
            sijainti, rotation = get_kortin_paikka(gui_pelipoyta, pelaaja, i)

            draw_card(surface, card, sijainti, CARD_WIDTH, CARD_HEIGHT, kortit_sheet, rotation=rotation)

def draw_bottom_player(gui_pelipoyta):  
    '''Piirtää ruudun alalaidassa olevan pelaajan, eli ihmispelaajan oman pelaajan.'''

    surface = gui_pelipoyta.screen
    pelaaja = gui_pelipoyta.nakyma
    valintapaneeli = gui_pelipoyta.valintapaneeli
    kortit_sheet = gui_pelipoyta.kortit_sheet

    #Pelaajapaneeli
    panel_x = PLAYER_GROUP_LEFT

    panel_rect = pygame.Rect(panel_x, 605, PLAYER_PANEL_WIDTH, PLAYER_PANEL_HEIGHT)

    draw_player_panel(surface, pelaaja, panel_rect)

    #Kortit
    if pelaaja.aktiivinen and not pelaaja.folded:
        for i, kortti in enumerate(pelaaja.kasikortit):

            selected = i in valintapaneeli.valitutKortit

            sijainti, rotation = get_kortin_paikka(gui_pelipoyta, pelaaja, i)

            if selected:  # Nostetaan valittuja kortteja
                sijainti = (sijainti[0], sijainti[1] - 10)

            rect = draw_card(surface, kortti, sijainti, CARD_WIDTH, CARD_HEIGHT, kortit_sheet, selected=selected)

            valintapaneeli.kortti_rectit[i] = rect

#Keskialue, logi ym muut lisätietoikkunat
def draw_center_area(gui_pelipoyta):
    '''Piirtää pelipöydän keskiosan, sisältäen mm. pakan, potin tiedot, logi-ruudun'''
    surface = gui_pelipoyta.screen
    nakyma = gui_pelipoyta.nakyma
    kortit_sheet = gui_pelipoyta.kortit_sheet

    #Logi, noin 5 riviä tekstiä (lisää? scroll bar?)
    log_height = 105
    log_bottom = 712

    log_rect = pygame.Rect(15, log_bottom - log_height, 320, log_height)

    draw_panel(surface, log_rect)

    messages = nakyma.log[-5:]  # 5 uusinta merkintää näkyy

    y = log_rect.y + 10

    for message in reversed(messages):

        draw_text(surface, message, (log_rect.x + 10, y), small_font)
        y += 18

    #Potti info
    pot_x = 620
    pot_y = 300

    draw_centered_text(surface, "POTTI", (pot_x, pot_y), large_font)

    if nakyma.potti is not None:
        draw_centered_text(surface, nakyma.potti, (pot_x, pot_y + 44), very_large_font, GOLD)

    if nakyma.suurinKorotus is not None:
        draw_centered_text(surface,
            f"Suurin korotus: {nakyma.suurinKorotus}",
            (pot_x, pot_y + 80), small_font, GRAY)

    #Pakka
    deck_x = DECK_X
    deck_y = DECK_Y

    for offset in [8, 4, 0]:

        draw_card(surface, "alaspain", (deck_x + offset, deck_y + offset), 78, 108, kortit_sheet)

    draw_centered_text(surface,
        "PAKKA",
        (deck_x, deck_y + 72), small_font)

#Yläpalkki, vähemmän relevanttia infoa
def draw_top_bar(gui_pelipoyta):
    '''Piirtää ruudun yläosassa olevan paneelin perustietoineen'''

    surface = gui_pelipoyta.screen
    nakyma = gui_pelipoyta.nakyma

    pygame.draw.rect(surface, PANEL_DARK, (0, 0, WIDTH, TOP_BAR_HEIGHT) )

    draw_text(surface,
        "POKERISIMULAATTORI",
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

    pygame.draw.rect(surface, RED, gui_pelipoyta.poistu_rect)

    draw_centered_text(
        surface,
        "POISTU",
        gui_pelipoyta.poistu_rect.center,
        font,
        WHITE
    )



#Pelaajapaneeli

def draw_player_panel(surface, pelaaja, rect):
    '''Piirtää pelaajalle inforuudun, jossa mm. tieto viimeisimmistä valinnoista, pelimerkkien määrästä, onko all-in ym.'''

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

    if pelaaja.aktiivinen:  #TÄHÄN SE VUOROSSA TÄGI, tai kokonaan veks vaan?
        pass

        #draw_text(surface, "● VUOROSSA", (rect.x + 10, rect.bottom - 20), small_font, GOLD)


# KORTTI


def create_card_surface(kortti, width, height, kortit_sheet, selected=False):
    '''Kortin pinnan piirtäminen.'''

    
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
    '''Kortin piirtäminen'''

    if kortti is not None:
        card_surface = create_card_surface(kortti, width, height, kortit_sheet, selected)

        if rotation != 0:
            card_surface = pygame.transform.rotate(card_surface, rotation)

        rect = card_surface.get_rect(center=center)

        surface.blit(card_surface, rect)

        return rect


def get_kortin_kuva(kortti, kortit_sheet, tausta=2):  
    '''Hakee kortin kuvan kortit_sheet tiedostosta. Leikkaa oikean kortin kuvan perustuen maahan ja kortin numeroon.
    Kortin tausta kovakoodattu, vaihtoehtoina 2, 3, 4, 5 ja 14 (koska sarake 1 = ässä = haussa numero 14)'''

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
