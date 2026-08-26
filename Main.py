from Pakka import Pakka, Kortti
from Pistelasku import laskeArvot
from Pelaaja import Pelaaja
from Pelipoyta import Pelipoyta
from GUI.GUI import GUI



testilista = []
asetukset = [{"aggressiivisuus": 1}, {"aggressiivisuus": 2}, {"aggressiivisuus": 3}]
ai_type = ["montecarlo", "montecarlo", "montecarlo"]
testilista.append(Pelaaja("IHMINEN", "Ihminen"))
for i in range(3):
    nimi = f"Tietokone {i+1}"
    tyyppi = "Tietsikka"
    testilista.append(Pelaaja(nimi, tyyppi, AI_valinta=ai_type[i], AI_asetukset=asetukset[i]))

ManualGame = Pelipoyta(testilista)
ManualGame.paivitaNakymat()


#ManualGame.testiPeli()  #Täysi pelit chipit nolliin

#Päivitä näkymään valmiiksi mahdollisuudet maksaa betit ja niiden summat, niin sitten ne voi implementoida GUI:hin suoraan ilman laskentaa


class Peli:

    def __init__(self, pelipoyta, gui=None):
        self.pelipoyta = pelipoyta
        self.gui = gui
        self.running = True

    def paivitaTila(self):
        if self.pelipoyta.tila == "valmis":
            #self.running = False
            return

        self.pelipoyta.paivitaTila()



peli = Peli(ManualGame)
peli.gui = GUI(testilista[0], peli)
testilista[0].gui = peli.gui
dt = 0

while peli.running:

    peli.paivitaTila()

    peli.gui.process_events()
    peli.gui.paivita(dt)  #fps
    peli.gui.draw()
    

    dt = peli.gui.clock.tick(60) / 1000

