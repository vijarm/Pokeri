import pygame
from . import settings
from .animaatiot import FoldAnimaatio, Korttijako, PelaajaIlmoitus, OdotusAnimaatio, VaihtoAnimaatio
from .piirtofunktiot import piirra_pelipoyta, draw_card, draw_centered_text, draw_panel, draw_player_panel, draw_text

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

CARD_WIDTH = 78
CARD_HEIGHT = 108
CARD_GAP = 8

# ============================================================
# VÄRIT
# ============================================================

TABLE_GREEN = settings.TABLE_GREEN
TABLE_DARK = settings.TABLE_DARK

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

font = settings.font
medium_font = settings.medium_font
large_font = settings.large_font



class GUI_pelipoyta:

    def __init__(self, screen, nakyma, kortit_sheet, lisaaKomento):
        self.screen = screen
        self.kortit_sheet = kortit_sheet
        self.nakyma = nakyma
        self.lisaaKomento = lisaaKomento
        self.valintapaneeli = ValintaPaneeli(nakyma, kortit_sheet, lisaaKomento)
        self.animaatiot = []

        self.poistu_rect = pygame.Rect(WIDTH - 120, 10, 100, 32)

    def handle_event(self, event):
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.poistu_rect.collidepoint(event.pos):
                self.lisaaKomento("poistu", self.nakyma.nimi)
                return
    
        self.valintapaneeli.handle_event(event)

    def asetaNakyma(self, uusinakyma):
        self.nakyma = uusinakyma
        self.valintapaneeli.nakyma = uusinakyma

    def handle_tapahtuma(self, tapahtuma):
        if tapahtuma["tapahtuma"] == "fold_voitto":
            self.valintapaneeli.mode = "fold_voitto"
            self.valintapaneeli.showdownData = tapahtuma["showdownData"]

        if tapahtuma["tapahtuma"] == "jaaKortit":
            self.valintapaneeli.showdownData = None
            self.valintapaneeli.mode = "odottaa"
            self.jaaKortit()

        if tapahtuma["tapahtuma"] == "panostus":
            self.valintapaneeli.mode = "odottaa"
            if tapahtuma["valinta"] == 4:  #fold
                self.foldaa(tapahtuma["pelaaja"])
            else:
                self.pelaajaIlmoitus(tapahtuma["pelaaja"], tapahtuma["ilmoitus"])

        if tapahtuma["tapahtuma"] == "pyydaPanos":
            if tapahtuma["pelaaja"] == self.nakyma.nimi:
                self.valintapaneeli.mode = "panostus"
            else:
                self.valintapaneeli.mode = "odottaa"

        if tapahtuma["tapahtuma"] == "pyydaVaihdot":
            if tapahtuma["pelaaja"] == self.nakyma.nimi:
                self.valintapaneeli.mode = "vaihdot"
            else:
                self.valintapaneeli.mode = "odottaa"

        if tapahtuma["tapahtuma"] == "korttivaihto":

            self.vaihdaKortit(tapahtuma["pelaaja"], tapahtuma["vaihtoindeksit"])

            teksti = ""
            if len(tapahtuma["vaihtoindeksit"]) == 1:
                teksti = "Vaihdan 1 kortin!"
            elif len(tapahtuma["vaihtoindeksit"]) == 0:
                teksti = "En vaihda mitään!"
            else: 
                teksti = f"Vaihdan {len(tapahtuma["vaihtoindeksit"])} korttia!"

            self.pelaajaIlmoitus(tapahtuma["pelaaja"], teksti)

        if tapahtuma["tapahtuma"] == "aloitaShowdown":
            self.valintapaneeli.showdownData = None
            self.valintapaneeli.mode = "showdown"

        if tapahtuma["tapahtuma"] == "showdownData":
            self.valintapaneeli.showdownData = tapahtuma["showdownData"]

        if tapahtuma["tapahtuma"] == "pelaajaTippui":
            self.yleisIlmoitus(2.5, tapahtuma["ilmoitus"])
            self.pelaajaIlmoitus(tapahtuma["pelaaja"], "Se oli siinä!")

        if tapahtuma["tapahtuma"] == "pelaajailmoitus":
            self.valintapaneeli.mode = "odottaa"
            self.pelaajaIlmoitus(tapahtuma["pelaaja"], tapahtuma["ilmoitus"])

        if tapahtuma["tapahtuma"] == "yleisilmoitus":
            self.yleisIlmoitus(1.8, tapahtuma["ilmoitus"])

        if tapahtuma["tapahtuma"] == "voittajaLoytyi":
            self.valintapaneeli.ilmoitus = tapahtuma["ilmoitus"]
            self.pelaajaIlmoitus(tapahtuma["pelaaja"], "JII HAA!!")
            self.valintapaneeli.mode = "voittajaLoytyi"

                                       
    def draw(self): 
        
        pygame.display.set_caption(
            "POKERISIMULAATTORI"
        )

        self.screen.fill(TABLE_DARK)

        piirra_pelipoyta(self)

        self.valintapaneeli.draw(self.screen) #Valintapaneelin sisältö muuttuu pelitilanteen mukaan

        for animaatio in self.animaatiot:
            animaatio.draw()



    #Animaatiofunktiot

    def jaaKortit(self):
        jakoAnimaatio = Korttijako(self)
        jakoAnimaatio.aloitaJako()
        self.animaatiot.append(jakoAnimaatio)

    def vaihdaKortit(self, pelaaja, indeksit):
        vaihtoAnimaatio = VaihtoAnimaatio(self, pelaaja, indeksit)
        vaihtoAnimaatio.aloita()
        self.animaatiot.append(vaihtoAnimaatio)

    def foldaa(self, pelaaja):
        foldAnimaatio = FoldAnimaatio(self, pelaaja)
        foldAnimaatio.aloita()
        self.animaatiot.append(foldAnimaatio)
        self.pelaajaIlmoitus(pelaaja, "Luovutan!")

    def pelaajaIlmoitus(self, pelaaja, teksti):
        self.animaatiot.append(PelaajaIlmoitus(self, self.haePelaajanPaikka(pelaaja), teksti))

    def yleisIlmoitus(self, aika, teksti):
        self.valintapaneeli.ilmoitus = teksti
        self.valintapaneeli.mode = "ilmoitus"
        self.animaatiot.append(OdotusAnimaatio(self, aika))

        
    def haePelaajanPaikka(self, pelaaja):  #Hakee nimen perusteella pelaajan paikan (0 = bottom, 1 = left, 2 = top, 3 = right)
        pelaajat = [self.nakyma] + self.nakyma.muutPelaajat
        pelaajaIndex = pelaajat.index(next(p for p in pelaajat if p.nimi == pelaaja))
        return pelaajaIndex


                        

# ============================================================
# VALINTAPANEELI, TÄSSÄ TAPAHTUU PELAAJAN VALINNAT
# ============================================================

class ValintaPaneeli:

    def __init__(self, nakyma, kortit_sheet, lisaaKomento):

        # "panostus"
        # "vaihdot"
        # "showdown"
        # "..."

        self.left = 390
        self.top = 465
        self.width = 500
        self.height = 120
        
        self.nakyma = nakyma
        self.mode = "odottaa"
        self.kortit_sheet = kortit_sheet

        self.valinta: str | None = None

        self.vaihdettavat: list | None = None
        self.valitutKortit = []
        self.kortti_rectit = {}

        self.ilmoitus = [] #Yksi listan alkio = yksi rivi ilmoitustekstiä

        self.showdownData = None

        self.lisaaKomento = lisaaKomento

        self.panostus_buttons = {
            "maksa": pygame.Rect(402, 540, 110, 35),
            "pieniKorotus": pygame.Rect(524, 540, 110, 35),
            "suuriKorotus": pygame.Rect(646, 540, 110, 35),
            "luovuta": pygame.Rect(768, 540, 110, 35),
        }

        self.vaihtoNappi_rect = pygame.Rect(570, 540, 140, 35)  #Yhdistetään napit, yksi OK??

        self.jatkaNappi_rect = pygame.Rect(585, 540, 110, 35)


    def handle_event(self, event):

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if self.mode == "odottaa":
            return

        elif self.mode == "ilmoitus":
            return

        elif self.mode == "panostus":

            for valinta, rect in self.panostus_buttons.items():

                if rect.collidepoint(event.pos):
                    if self.valintaSallittu(valinta):
                        self.lisaaKomento("panostusvalinta", self.nakyma.nimi, {"panostusvalinta": valinta})
                        self.mode = "odottaa"

        elif self.mode == "vaihdot":

            if event.type == pygame.MOUSEBUTTONDOWN:

                for i, rect in self.kortti_rectit.items():

                    if rect.collidepoint(event.pos):

                        if i in self.valitutKortit:
                            self.valitutKortit.remove(i)
                        else:
                            self.valitutKortit.append(i)
                        return

                if self.vaihtoNappi_rect.collidepoint(event.pos):  #Kun painetaan vaihda-nappia

                    self.lisaaKomento("vaihdot", self.nakyma.nimi, {"vaihtoindeksit": self.valitutKortit.copy()})
                    self.valitutKortit = []
                    self.mode = "odottaa"
                    return
                                       

        elif self.mode == "showdown":

            if event.type == pygame.MOUSEBUTTONDOWN:

                if self.jatkaNappi_rect.collidepoint(event.pos):
                    self.lisaaKomento("ok", self.nakyma.nimi)

        elif self.mode == "fold_voitto":

            if event.type == pygame.MOUSEBUTTONDOWN:

                if self.jatkaNappi_rect.collidepoint(event.pos):
                    #self.jatketaan = True
                    self.lisaaKomento("ok", self.nakyma.nimi)
                    self.mode = "odottaa"

        elif self.mode == "voittajaLoytyi":

            if event.type == pygame.MOUSEBUTTONDOWN:

                if self.jatkaNappi_rect.collidepoint(event.pos):
                    self.lisaaKomento("peli_ohi", self.nakyma.nimi)
                    #Engine vaihtaa valikkoon

                
    def draw(self, surface):

        rect = pygame.Rect(self.left, self.top, self.width, self.height)

        draw_panel(surface, rect, GOLD)

        if self.mode == "odottaa": 

            draw_centered_text(surface, 
                "Odotetaan...",   
                (rect.centerx, rect.y + 35), medium_font, GRAY)

        elif self.mode == "ilmoitus":

            for rivi in range(len(self.ilmoitus)):

                draw_centered_text(surface,
                    self.ilmoitus[rivi],
                    (rect.centerx, rect.y + 22 + (rivi * 25)), medium_font)


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

            teksti = ""
            if len(self.valitutKortit) == 1:
                teksti = "Vaihda 1 kortti"
            else:
                teksti = f"Vaihda {len(self.valitutKortit)} korttia"

            draw_centered_text(surface,
                teksti,
                self.vaihtoNappi_rect.center, font, BLACK)

        elif self.mode == "showdown":

            draw_centered_text(surface, 
                "PARAS KÄSI VOITTAA", 
                (rect.centerx, rect.y + 30), large_font)

            pygame.draw.rect(surface, GOLD, self.jatkaNappi_rect)

            draw_centered_text(surface, "JATKA", self.jatkaNappi_rect.center, font, BLACK)

            if self.showdownData is not None:
                self.piirraShowdown(surface)

        elif self.mode == "fold_voitto":

            assert self.showdownData is not None

            voittaja = self.showdownData
            draw_centered_text(surface,
                "MUUT PELAAJAT LUOVUTTIVAT",
                (rect.centerx, rect.y + 30), medium_font)

            draw_centered_text(surface,
                f"{voittaja["voittaja"]} voitti {voittaja["potti"]} merkkiä!",
                (rect.centerx, rect.y + 50), medium_font)

            pygame.draw.rect(surface, GOLD, self.jatkaNappi_rect)

            draw_centered_text(surface, "JATKA", self.jatkaNappi_rect.center, font, BLACK)

        elif self.mode == "voittajaLoytyi":
    
                for rivi in range(len(self.ilmoitus)):
    
                    draw_centered_text(surface,
                        self.ilmoitus[rivi],
                        (rect.centerx, rect.y + 15 + (rivi * 25)), medium_font)

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
                return f"Korota {nakyma.pieniKorotus}"
            
            if valinta == "suuriKorotus":
                return f"Korota {nakyma.suuriKorotus}"

            if valinta == "luovuta":
                return "Luovuta"

    def piirraShowdown(self, surface):

        assert self.showdownData is not None, "ShowdownData puuttuu"

        rect = pygame.Rect(CENTER_LEFT + 80, TOP_BAR_HEIGHT + 150, CENTER_WIDTH - 160, 250)
        
        draw_panel(surface, rect, GOLD)

        showdown = self.showdownData

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
