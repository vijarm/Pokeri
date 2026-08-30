from Pakka import Pakka, Kortti
from Pistelasku import laskeArvot
from Pelaaja import Pelaaja
from Pelipoyta import Pelipoyta
from GUI.GUI import GUI
from transport import LocalTransport, NetworkTransport



testilista = []
asetukset = [{"aggressiivisuus": 1, "luokka": "Monte Carlo"}, {"aggressiivisuus": 2, "luokka": "Monte Carlo"}, {"aggressiivisuus": 3, "luokka": "Monte Carlo"}]
ai_type = ["Monte Carlo", "Monte Carlo", "Monte Carlo"]
testilista.append(Pelaaja("IHMINEN", "Ihminen"))
for i in range(3):
    nimi = f"Tietokone {i+1}"
    tyyppi = "Tietsikka"
    testilista.append(Pelaaja(nimi, tyyppi, AI_valinta=ai_type[i], AI_asetukset=asetukset[i]))

ManualGame = Pelipoyta(testilista)
ManualGame.paivitaNakymat()


#ManualGame.testiPeli()  #Täysi pelit chipit nolliin



class Peli:

    def __init__(self, gui=None):
        self.pelipoyta = None
        self.gui = gui
        self.running = True
        self.mode = "valikko"
        self.komennot = []  #GUI:sta enginelle tulevat
        self.menu_paivitykset = []  #Valikosta GUI:lle siirtyvät
        self.ihmispelaajat = []
        self.transport = LocalTransport()

    def paivitaTila(self):

        if self.mode == "pelipoyta":
            if self.pelipoyta is not None:
                if self.pelipoyta.tila == "valmis":
                    #self.mode = "valikko" vaihdetaan komennolla, kun GUI on painanut ok
                    self.paivitys_to_gui("vaihda_gui_mode", "valikko")
                    return

                self.pelipoyta.paivitaTila()

    def kasitteleKomento(self, komento):

        if self.mode == "valikko":

            if komento.tapahtuma == "muokkaa_pelaajaa":
                komento.pelaaja.muokkaa(komento.tiedot)        
                return

            elif komento.tapahtuma == "luo_pelaaja":
                pelaaja = self.luoPelaaja(komento.tiedot)
                self.menu_paivitys("uusipelaaja", {"pelaaja": pelaaja, "indeksi": komento.tiedot["indeksi"]})
                return            

            elif komento.tapahtuma == "sulje_peli":
                self.running = False
                return

            elif komento.tapahtuma == "aloita_peli":
                self.pelipoyta = Pelipoyta([p for p in komento.pelaaja if p is not None])
                self.pelipoyta.paivitaNakymat()
                self.mode = "pelipoyta"
                self.paivitys_to_gui("vaihda_gui_mode", "pelipoyta")
                self.menu_paivitys("uusipeli", self.pelipoyta)  #Tää poistuu kun pelipöytä poistuu guista
                return


        if self.mode == "pelipoyta":
            
            assert self.pelipoyta is not None

            if komento.tapahtuma == "vaihdot":
                if komento.pelaaja != self.pelipoyta.jako.vaihtoPelaaja.nimi:
                    print("Väärä pelaaja yritti vaihtaa kortteja")
                    return

                self.pelipoyta.jako.vaihtoindeksit = komento.tiedot["vaihtoindeksit"]

            elif komento.tapahtuma == "poistu":
                self.mode = "valikko"
                self.paivitys_to_gui("vaihda_gui_mode", "valikko")
                self.pelipoyta = None  #Vai halutaanko että voi jatkaa
                print(f"Pelaaja {komento.pelaaja} poistui pelistä.")

            elif komento.tapahtuma == "ok":
                self.pelipoyta.ok = True
                print(f"Pelaaja {komento.pelaaja} painoi OK.")

            elif komento.tapahtuma == "panostusvalinta":
                if komento.pelaaja != self.pelipoyta.jako.panostuskierros.pelaajaVuorossa.nimi:
                    print("Väärä pelaaja yritti antaa panostusvalintaa")
                    return
                
                self.pelipoyta.jako.panostuskierros.panostusValinta = komento.tiedot["panostusvalinta"]

            elif komento.tapahtuma == "peli_ohi":
                self.mode = "valikko"
                self.paivitys_to_gui("vaihda_gui_mode", "valikko")
                self.pelipoyta = None



    def luoPelaaja(self, tiedot):
        if tiedot["ai"] is not None:
            asetukset = {"aggressiivisuus": tiedot["ai_aggressiivisuus"], "luokka": tiedot["ai"], "strategia": tiedot["ai_strategia"]}
            return Pelaaja(tiedot["nimi"], tiedot["tyyppi"], tiedot["ai"], asetukset)

        else:
            return Pelaaja(tiedot["nimi"], tiedot["tyyppi"])

    def menu_paivitys(self, tyyppi, tiedot):
        self.menu_paivitykset.append(Paivitys(tyyppi, tiedot))

    def haeMenuPaivitykset(self):
        paivitykset = self.menu_paivitykset
        self.menu_paivitykset = []
        return paivitykset

    def paivitys_to_gui(self, tyyppi, tiedot, nakyma=None):
        paivitys = Paivitys(tyyppi, tiedot, nakyma)
        self.transport.send_to_gui(paivitys)




class Paivitys:
    def __init__(self, tyyppi, tiedot, nakyma=None):
        self.tyyppi = tyyppi
        self.tiedot = tiedot
        self.nakyma = nakyma

    def to_dict(self):
        return {
            "otsikko": "Paivitys",
            "tyyppi": self.tyyppi,
            "tiedot": self.tiedot,
            "nakyma": self.nakyma
        }

    @classmethod
    def from_dict(cls, data):
        return cls(tyyppi = data["tyyppi"],
            tiedot = data["tiedot"],
            nakyma = data["nakyma"])
    #Ja sitten jos on sisäkkäisiä olioita, niin ne täytyy muuttaa todict ennen lisäämistä



peli = Peli(ManualGame)
peli.gui = GUI(testilista[0], peli, peli.transport)
testilista[0].gui = peli.gui
dt = 0

while peli.running:

    peli.gui.process_events()

    komennot = peli.gui.haeKomennot()
    for komento in komennot:
        peli.kasitteleKomento(komento)

    peli.paivitaTila()
    peli.gui.paivita(dt)  #fps
    peli.gui.draw()

    dt = peli.gui.clock.tick(60) / 1000

