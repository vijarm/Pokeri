import pygame
from . import settings

#Tää koko höskä nostetaan class GUI sisään, jossa initissä syötetään pelaaja, ja aletaan sijottamaan pelaaja.nakymaa

'''oo. Tässä kannattaa muistaa yksi hyvin yksinkertainen kaava:

nappi = Rect + piirto + hiiren osuman tarkistus + toiminto.

Tavallinen nappi
button_rect = pygame.Rect(500, 500, 120, 50)


def draw_button(screen, rect, text, selected=False):

    # Väri vaihtuu valinnan mukaan
    if selected:
        color = (220, 180, 50)       # highlight
    else:
        color = (60, 70, 70)

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        (255, 255, 255),
        rect,
        width=2,
        border_radius=8
    )

    text_surface = font.render(
        text,
        True,
        (255, 255, 255)
    )

    text_rect = text_surface.get_rect(
        center=rect.center
    )

    screen.blit(
        text_surface,
        text_rect
    )

Event-loopissa:

for event in pygame.event.get():

    if event.type == pygame.MOUSEBUTTONDOWN:

        if button_rect.collidepoint(event.pos):

            # TÄHÄN napin toiminto
            print("CALL painettu")

Eli myöhemmin:

if button_rect.collidepoint(event.pos):
    return 1

ja Engine saa 1.

Useampi nappi
call_rect = pygame.Rect(400, 500, 100, 45)
raise_rect = pygame.Rect(510, 500, 100, 45)
fold_rect = pygame.Rect(620, 500, 100, 45)

if event.type == pygame.MOUSEBUTTONDOWN:

    if call_rect.collidepoint(event.pos):
        return 1

    elif raise_rect.collidepoint(event.pos):
        return 2

    elif fold_rect.collidepoint(event.pos):
        return 4

Kortin selected-tila
Tämä on käytännössä sama mekanismi.

Kortilla on Rect:

card_rect = pygame.Rect(
    500,
    600,
    78,
    108
)

Ja oma tila:

selected = False

Piirretään kortti eri tavalla riippuen tilasta:

if selected:
    border_color = (230, 190, 40)
    border_width = 5
else:
    border_color = (20, 20, 20)
    border_width = 2


pygame.draw.rect(
    screen,
    (255, 255, 255),
    card_rect,
    border_radius=7
)

pygame.draw.rect(
    screen,
    border_color,
    card_rect,
    width=border_width,
    border_radius=7
)

Klikkaus vaihtaa tilan:

if event.type == pygame.MOUSEBUTTONDOWN:

    if card_rect.collidepoint(event.pos):

        selected = not selected

Nyt:

ei valittu:

┌─────────┐
│         │
│    A♠   │
│         │
└─────────┘


valittu:

╔═════════╗
║         ║
║   A♠    ║
║         ║
╚═════════╝
    ↑
 highlight

Usealle kortille
Tämä on sinun pokeripelissäsi olennaisin:

selected_cards = []

Klikattaessa:

if card_rect.collidepoint(event.pos):

    if card in selected_cards:
        selected_cards.remove(card)
    else:
        selected_cards.append(card)

Ja piirtäessä:

selected = card in selected_cards

draw_card(
    screen,
    card,
    rect,
    selected=selected
)

Kun VAIHDA painetaan:

if vaihda_rect.collidepoint(event.pos):

    return selected_cards

Eli tämän voi oikeastaan muistaa yhtenä kaavana:

PIIRRÄ
  ↓
Rect
  ↓
TARKISTA:
collidepoint(event.pos)
  ↓
MUUTA TILAA / SUORITA TOIMINTO
  ↓
SEURAAVA FRAME PIIRTÄÄ UUDEN TILAN

Tuo viimeinen kohta on Pygamessa tärkeä: et yleensä "muokkaa ruudulla olevaa nappia". Muutat esimerkiksi selected = True, ja seuraavalla renderöintikierroksella nappi/kortti piirretään highlightattuna.'''


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

GOLD = settings.GOLD

small_font = settings.small_font
font = settings.font
medium_font = settings.medium_font
large_font = settings.large_font
title_font = settings.title_font




def GUI_pelipoyta(screen, valintapaneeli, pelaaja):
    
    nakyma = pelaaja  #Gui siis lähettää suoraan pelaaja.nakyma, jossa on kaikki piirtoon tarvittavat data


    pygame.display.set_caption(
        "POKERISIMULAATTORI"
    )

    screen.fill(TABLE_GREEN)


    draw_top_bar(
        screen,
        nakyma
    )

    draw_bottom_player(  #Oma pelaaja
        screen,
        nakyma,
        valintapaneeli
    )

    draw_side_player(
        screen,
        nakyma.muutPelaajat[0],
        "left"
    )

    draw_top_player(
        screen,
        nakyma.muutPelaajat[1]
    )

    draw_side_player(
        screen,
        nakyma.muutPelaajat[2],
        "right"
    )

    draw_center_area(
        screen,
        nakyma
    )

    valintapaneeli.draw(  #Aktiivinen valintapaneeli, valinnat pelitilanteen mukaan
        screen
    )

'''
    gui_nakyma = {

        "kierros": nakyma.kierros,
        "vaihe": "nakyma.pelivaihe",
        "jakaja": "nakyma.jakaja",

        "potti": nakyma.potti,
        "korotus": nakyma.suurinKorotus,

        "pelaajat": [

            # ----------------------------------------------------
            # P1 = aktiivinen / ihmispelaaja
            # ----------------------------------------------------

            {
                "nimi": nakyma.nimi,
                "chips": nakyma.chips,
                "maksettuJakoon": nakyma.maksettuJakoon,
                "valinta": nakyma.valinta,
                "kortit": nakyma.kasikortit,
                "vuorossa": True,
            },

            # ----------------------------------------------------
            # P2 = vasen
            # ----------------------------------------------------

            {
                "nimi": muutPelaajat[0].nimi,
                "chips": muutPelaajat[0].chips,
                "maksettuJakoon": muutPelaajat[0].maksettuJakoon,
                "valinta": "Raise",
                "kortit": ["?", "?", "?", "?", "?"],
                "vuorossa": False,
            },

            # ----------------------------------------------------
            # P3 = ylhäällä
            # ----------------------------------------------------

            {
                "nimi": muutPelaajat[1].nimi,
                "chips": muutPelaajat[1].chips,
                "maksettuJakoon": muutPelaajat[1].maksettuJakoon,
                "valinta": "Raise",
                "kortit": ["?", "?", "?", "?", "?"],
                "vuorossa": False,
            },

            # ----------------------------------------------------
            # P4 = oikealla
            # ----------------------------------------------------

            {
                "nimi": muutPelaajat[2].nimi,
                "chips": muutPelaajat[2].chips,
                "maksettuJakoon": muutPelaajat[2].maksettuJakoon,
                "valinta": "Raise",
                "kortit": ["?", "?", "?", "?", "?"],
                "vuorossa": False,
            },
        ],

        "log": [
            "Kortit jaettu.",
            "Pelaaja 2 maksaa 20.",
            "Pelaaja 3 maksaa 20.",
            "Pelaaja 4 korottaa 20.",
            "Pelaaja 1 maksaa 40.",
        ],
    }
    '''


# ============================================================
# APUTOIMINNOT
# ============================================================

def draw_text(
    surface,
    text,
    position,
    font_object=font,
    color=WHITE
):
    rendered = font_object.render(
        str(text),
        True,
        color
    )

    surface.blit(
        rendered,
        position
    )


def draw_centered_text(
    surface,
    text,
    center,
    font_object=font,
    color=WHITE
):
    rendered = font_object.render(
        str(text),
        True,
        color
    )

    rect = rendered.get_rect(
        center=center
    )

    surface.blit(
        rendered,
        rect
    )


def draw_panel(
    surface,
    rect,
    border_color=LIGHT_GRAY
):
    pygame.draw.rect(
        surface,
        PANEL_COLOR,
        rect,
        border_radius=8
    )

    pygame.draw.rect(
        surface,
        border_color,
        rect,
        width=2,
        border_radius=8
    )


# ============================================================
# YLÄPALKKI
# ============================================================

def draw_top_bar(
    surface,
    nakyma
):

    pygame.draw.rect(
        surface,
        PANEL_DARK,
        (0, 0, WIDTH, TOP_BAR_HEIGHT)
    )

    draw_text(
        surface,
        "5 CARD DRAW TESTITESTINEN",
        (18, 13),
        title_font
    )

    draw_text(
        surface,
        f"Jako {nakyma.kierros}",
        (400, 17)
    )

    draw_text(
        surface,
        f"Pelivaihe: {PELIVAIHE[nakyma.pelivaihe]}",
        (515, 17)
    )

    draw_text(
        surface,
        f"Jakaja: {nakyma.jakaja}",
        (790, 17)
    )


# ============================================================
# PELAAJAPANEELI
# ============================================================

def draw_player_panel(
    surface,
    pelaaja,
    rect
):
    border_color = (
        GOLD
        if pelaaja.aktiivinen  # OIKEESTI pitää lisätä joku vuorossa tägi pelaajille
        else LIGHT_GRAY
    )

    draw_panel(
        surface,
        rect,
        border_color
    )

    draw_text(
        surface,
        pelaaja.nimi,
        (
            rect.x + 10,
            rect.y + 8
        ),
        medium_font
    )

    draw_text(
        surface,
        f"Chips: {pelaaja.chips}",
        (
            rect.x + 10,
            rect.y + 37
        ),
        small_font
    )

    draw_text(
        surface,
        f"Potissa: {pelaaja.maksettuJakoon}",
        (
            rect.x + 10,
            rect.y + 57
        ),
        small_font
    )

    draw_text(
        surface,
        VALINNAT[pelaaja.valinta],  #Pitää vähän suomentaa valintoja numeroista
        (
            rect.x + 10,
            rect.y + 77
        ),
        small_font
    )

    if pelaaja.aktiivinen:  #TÄHÄN SE VUOROSSA TÄGI

        draw_text(
            surface,
            "● VUOROSSA",
            (
                rect.x + 10,
                rect.bottom - 20
            ),
            small_font,
            GOLD
        )


# ============================================================
# KORTTI
# ============================================================

def create_card_surface(
    card,
    width,
    height,
    selected=False
):
    card_surface = pygame.Surface(
        (width, height),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        card_surface,
        WHITE,
        (0, 0, width, height),
        border_radius=7
    )

    border_color = (
        GOLD
        if selected
        else BLACK
    )

    border_width = (
        4
        if selected
        else 2
    )

    pygame.draw.rect(
        card_surface,
        border_color,
        (0, 0, width, height),
        width=border_width,
        border_radius=7
    )

    draw_centered_text(
        card_surface,
        card,
        (width // 2, height // 2),
        medium_font,
        BLACK
    )

    return card_surface


def draw_card(
    surface,
    card,
    center,
    width,
    height,
    rotation=0,
    selected=False
):
    card_surface = create_card_surface(
        card,
        width,
        height,
        selected
    )

    if rotation != 0:

        card_surface = pygame.transform.rotate(
            card_surface,
            rotation
        )

    rect = card_surface.get_rect(
        center=center
    )

    surface.blit(
        card_surface,
        rect
    )

    return rect


# ============================================================
# YLÄPELIN / ALAPELIN YHTEINEN MITOITUS
# ============================================================
#
# Näin P1 ja P2 saadaan varmasti samalle vaakasuuntaiselle
# keskiviivalle.
#
# Kokonaisuus:
#
#   INFO | kortit
#
# on yhtä leveä sekä ylhäällä että alhaalla.
# ============================================================

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
# P2 — YLÄPELAAJA
# ============================================================

def draw_top_player(
    surface,
    pelaaja
):

    # --------------------------------------------------------
    # Sama kokonaisleveys kuin P1:llä.
    # --------------------------------------------------------

    panel_x = PLAYER_GROUP_LEFT

    cards_x = (
        panel_x
        + PLAYER_PANEL_WIDTH
        + 25
    )

    # P2:n paneeli
    panel_rect = pygame.Rect(
        panel_x,
        68,
        PLAYER_PANEL_WIDTH,
        PLAYER_PANEL_HEIGHT
    )

    draw_player_panel(
        surface,
        pelaaja,
        panel_rect
    )

    # --------------------------------------------------------
    # P2:n kortit
    # --------------------------------------------------------

    for i, card in enumerate(
        ["??", "??", "??", "??", "??"]   #TÄHÄN JOKU LINKKI tai cardcount pelaajalle tms, vai geneerisesti vaan
    ):

        x = (
            cards_x
            + i * (CARD_WIDTH + CARD_GAP)
            + CARD_WIDTH // 2
        )

        draw_card(
            surface,
            card,
            (
                x,
                121
            ),
            CARD_WIDTH,
            CARD_HEIGHT
        )


# ============================================================
# SIVUPELAAJAT
# ============================================================

def draw_side_player(
    surface,
    pelaaja,
    side
):
    """
    P3/P4:

    Kortit ovat täysin saman kokoisia kuin P1/P2:n kortit.

    Pyörityksen jälkeen niiden pystysuuntainen koko on
    CARD_WIDTH = 78 px.

    Step = 80 px -> vain 2 px visuaalinen väli.
    """

    if side == "left":

        panel_x = 15

        card_x = (
            SIDE_WIDTH // 2
        )

        rotation = 90

    else:

        panel_x = (
            WIDTH
            - SIDE_WIDTH
            + 15
        )

        card_x = (
            WIDTH
            - SIDE_WIDTH // 2
        )

        rotation = 270

    # --------------------------------------------------------
    # Pelaajapaneeli
    # --------------------------------------------------------

    panel_rect = pygame.Rect(
        panel_x,
        75,
        160,
        105
    )

    draw_player_panel(
        surface,
        pelaaja,
        panel_rect
    )

    # --------------------------------------------------------
    # Sivukortit
    # --------------------------------------------------------

    vertical_step = 80

    start_y = 230

    for i, card in enumerate(
        ["??", "??", "??", "??", "??"]   #TÄHÄN JOKU LINKKI tai cardcount pelaajalle tms, vai geneerisesti vaan
    ):

        y = (
            start_y
            + i * vertical_step
        )

        draw_card(
            surface,
            card,
            (
                card_x,
                y
            ),
            CARD_WIDTH,
            CARD_HEIGHT,
            rotation=rotation
        )


# ============================================================
# KESKIALUE
# ============================================================

def draw_center_area(
    surface,
    nakyma
):

    # --------------------------------------------------------
    # LOGI
    # --------------------------------------------------------
    #
    # Vain noin 5 riviä näkyviin.
    # Myöhemmin tähän scrollbar.
    # --------------------------------------------------------

    log_height = 105
    log_bottom = 712

    log_rect = pygame.Rect(
        15,
        log_bottom - log_height,
        270,
        log_height
    )

    draw_panel(
        surface,
        log_rect
    )

    draw_text(
        surface,
        "Tapahtumat",
        (
            log_rect.x + 12,
            log_rect.y - 10
        ),
        medium_font
    )

    messages = nakyma.log[-5:]

    y = log_rect.y + 10

    for message in reversed(messages):

        draw_text(
            surface,
            message,
            (
                log_rect.x + 10,
                y
            ),
            small_font
        )

        y += 18

    # --------------------------------------------------------
    # POTTI
    # --------------------------------------------------------

    pot_x = 620
    pot_y = 300

    draw_centered_text(
        surface,
        "POTTI",
        (
            pot_x,
            pot_y
        ),
        medium_font
    )

    draw_centered_text(
        surface,
        nakyma.potti,
        (
            pot_x,
            pot_y + 38
        ),
        large_font,
        GOLD
    )

    draw_centered_text(
        surface,
        f"Suurin korotus: {nakyma.suurinKorotus}",
        (
            pot_x,
            pot_y + 72
        ),
        small_font,
        GRAY
    )

    # --------------------------------------------------------
    # PAKKA
    # --------------------------------------------------------

    deck_x = 785
    deck_y = 320

    for offset in [8, 4, 0]:

        rect = pygame.Rect(
            deck_x - 39 + offset,
            deck_y - 54 + offset,
            78,
            108
        )

        pygame.draw.rect(
            surface,
            (35, 65, 110),
            rect,
            border_radius=7
        )

        pygame.draw.rect(
            surface,
            WHITE,
            rect,
            width=2,
            border_radius=7
        )

    draw_centered_text(
        surface,
        "PAKKA",
        (
            deck_x,
            deck_y + 72
        ),
        small_font
    )


# ============================================================
# VALINTAPANEELI, TÄSSÄ TAPAHTUU PELAAJAN TÄRKEIMMÄT VALINNAT
# ============================================================

class ValintaPaneeli:

    def __init__(self, pelaaja):

        # Myöhemmin näkymästä:
        #
        # "waiting"
        # "actions"
        # "exchange"
        # "continue"
        
        self.pelaaja = pelaaja
        self.mode = "panostus"

        self.valinta: str | None = None

        self.vaihdettavat: list | None = None
        self.valitutKortit = []
        self.kortti_rectit = {}

        self.jatketaan = None

        self.panostus_buttons = {
            "maksa": pygame.Rect(475, 490, 90, 35),
            "pieniKorotus": pygame.Rect(570, 490, 90, 35),
            "suuriKorotus": pygame.Rect(665, 490, 90, 35),
            "luovuta": pygame.Rect(760, 490, 90, 35),
        }

        self.vaihtoNappi_rect = pygame.Rect(620, 500, 100, 35)

        self.jatkaNappi_rect = pygame.Rect(620, 500, 100, 35)


    def handle_event(self, event):

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if self.mode == "panostus":

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



    def get_valinta(self):

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
            return jatketaan

                
    def draw(
        self,
        surface
    ):

        rect = pygame.Rect(
            475,
            455,
            390,
            80
        )

        draw_panel(
            surface,
            rect,
            GOLD
        )

        if self.mode == "waiting":

            draw_centered_text(
                surface,
                "Pelaaja 2:n vuoro",
                (
                    rect.centerx,
                    rect.y + 25
                ),
                medium_font
            )

            draw_centered_text(
                surface,
                "Odotetaan...",
                (
                    rect.centerx,
                    rect.y + 55
                ),
                small_font,
                GRAY
            )

        elif self.mode == "panostus":
            for valinta, rect in self.panostus_buttons.items():

                if self.valintaSallittu(valinta):  #Tarkistaa onko valinta mahdollinen
                    color = GOLD
                    text_color = BLACK

                else:
                    color = GRAY
                    text_color = LIGHT_GRAY

                pygame.draw.rect(
                    surface,
                    color,
                    rect
                )

                draw_centered_text(
                    surface,
                    self.valintaTeksti(valinta),
                    rect.center,
                    font,
                    text_color
                )

        elif self.mode == "vaihdot":

            draw_centered_text(
                surface,
                "VALITSE VAIHDETTAVAT KORTIT",
                (
                    rect.centerx,
                    rect.y + 20
                ),
                medium_font
            )

            pygame.draw.rect(
                surface, GOLD, self.vaihtoNappi_rect
            )

            draw_centered_text(
                surface,
                "[ VAIHDA ]",
                self.vaihtoNappi_rect.center,
                font,
                BLACK
            )

        elif self.mode == "showdown":

            draw_centered_text(
                surface,
                "Käsien vertailu",
                (
                    rect.centerx,
                    rect.y + 20
                ),
                medium_font
            )

            pygame.draw.rect(
                surface, GOLD, self.jatkaNappi_rect
            )

            draw_centered_text(
                surface,
                "[ JATKA ]",
                self.jatkaNappi_rect.center,
                font,
                BLACK
            )

    def valintaSallittu(self, valinta):  #Tässä on nyt noita is not None tsekkejä, lopullisessa versiossa niitä ei tarvita mutta nyt gui alkaa panostuksesta. Normaalisti ne on olemassa kun gui panostus starttaa
        nakyma = self.pelaaja.nakyma

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
        nakyma = self.pelaaja.nakyma
        if nakyma.maksettavaa is not None and nakyma.pieniKorotus is not None and nakyma.suuriKorotus is not None:
            if valinta == "maksa":
                if nakyma.maksettavaa == 0:
                    return "Check!"
                else:
                    return f"Maksa {nakyma.maksettavaa}"

            if valinta == "pieniKorotus":
                return f"Korota {nakyma.pieniKorotus} + maksa {nakyma.maksettavaa}\nYhteensä: {nakyma.pieniKorotus + nakyma.maksettavaa}"
            
            if valinta == "suuriKorotus":
                return f"Korota {nakyma.suuriKorotus} + maksa {nakyma.maksettavaa}\nYhteensä: {nakyma.suuriKorotus + nakyma.maksettavaa}"

            if valinta == "luovuta":
                return "Luovuta"




# ============================================================
# P1 — ALAPELAAJA
# ============================================================

def draw_bottom_player(
    surface,
    pelaaja,
    valintapaneeli
):

    panel_x = PLAYER_GROUP_LEFT

    cards_x = (
        panel_x
        + PLAYER_PANEL_WIDTH
        + 25
    )

    # --------------------------------------------------------
    # Info
    # --------------------------------------------------------

    panel_rect = pygame.Rect(
        panel_x,
        605,
        PLAYER_PANEL_WIDTH,
        PLAYER_PANEL_HEIGHT
    )

    draw_player_panel(
        surface,
        pelaaja,
        panel_rect
    )

    # --------------------------------------------------------
    # Kortit
    # --------------------------------------------------------

    for i, kortti in enumerate(pelaaja.kasikortit):

        selected = i in valintapaneeli.valitutKortit

        x = (
            cards_x
            + i * (CARD_WIDTH + CARD_GAP)
            + CARD_WIDTH // 2
        )

        rect = draw_card(
            surface,
            kortti,
            (x, 658),
            CARD_WIDTH,
            CARD_HEIGHT,
            selected=selected
        )

        valintapaneeli.kortti_rectit[i] = rect



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
