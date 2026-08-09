from Pistelasku import laskeArvot, haeVoittaja
from Pelaaja import Pelaaja

class Jako:
    def __init__(self, pelipakka, pelaajalista: list, alkupanos: int, jakaja: int):
        self.pakka = pelipakka
        self.pelaajat = pelaajalista
        self.potti = Potti(self.pelaajat, alkupanos)
        self.sivupotti = []
        self.jakaja = jakaja #Jakajan indeksi pelaajalistasta

        self.discardPile = [] #tarvitaanko, vai popataanko vaan veks?
        self.suurinKorotus: int = 0 # Jostain pitää saada ne min/max raiset, pelipöydästä Jaon kautta kierrettynä?

        self.pakka.sekoita()

    def pelaaKierros(self) -> tuple:
        self.jaaKortit()
        #panostuskierros
        #Tää toimii mutta pois jotta simuloi ympäriinsä:
        #for pelaaja in self.pelaajat:
        #    if pelaaja.aktiivinen:
        #        self.pyydaVaihto(pelaaja)
        #panostuskierros
        #jos päästään perille niin haevoittaja (alla), muuten jo aiemmin
        self.kerroKortit()
        voittaja = self.haeVoittaja()
        print("")
        print("Voittaja:", voittaja)
        return (voittaja, self.potti)


    def jaaKortit(self): 
        alkukadet = self.pakka.jaaKortit(len(self.pelaajat), 5)
        for i in range(len(alkukadet)):
            self.pelaajat[i].kasikortit = alkukadet[i]
    
    def kerroKortit(self):
        for pelaaja in self.pelaajat:
            print("Pelaaja:", pelaaja.nimi, "käsikortit: ", pelaaja.kasikortit)
        print ("Pakkaan jäi kortteja:", len(self.pakka.kortit))

    def vertaaKadet(self): #Tää poistuu koska on sama kuin pistelasku haeVoittaja?
        tulos = []
        voittaja = []
        for pelaaja in self.pelaajat:
            print(pelaaja.kasikortit)
            pisteet = laskeArvot(pelaaja.kasikortit)
            pisteet["pelaaja"] = pelaaja.nimi
            tulos.append(pisteet)
            if len(voittaja) == 0 or voittaja[0]["vahvuus"] == pisteet["vahvuus"]: 
                voittaja.append(pisteet)
            else: 
                if voittaja[0]["vahvuus"] < pisteet["vahvuus"]:
                    voittaja = [pisteet]
        tulos.sort(key=lambda p: p["vahvuus"], reverse=True)
        print (tulos)
        if len(voittaja) == 1:
            print ("VOITTAJA!!! Pelin voitti", voittaja[0]["pelaaja"], "kädessään", voittaja[0]["kasinimi"])
        else:
            print ("OHHHHOHHHHHHHHH TASAPELI!!! KATSOS:", voittaja)
        return voittaja
    
    def haeVoittaja(self) -> list:  #PelaajatMukana list tms?
        mukana = []
        for pelaaja in self.pelaajat:
            if pelaaja.aktiivinen: 
                mukana.append(pelaaja)
        return haeVoittaja(mukana)

    def pyydaVaihto(self, pelaaja: Pelaaja): #TÄHÄN sitten jotain, valitaan hiirellä, palauta lista
        while True:
            print(pelaaja.kasikortit)
            vaihdetaan = input("Mitä vaihdetaan indeksillä?")
            if vaihdetaan.strip() == "": break
            lista = vaihdetaan.split(" ")
            if len(lista) > 5: continue
            virhe = False
            for i in lista:
                if i not in "01234": 
                    virhe = True
                    break
            if virhe: continue
            #Tässä tapahtuu nyt se vaihto (yksi kerrallaan)
            for indeksi in sorted(lista, reverse=True):
                pelaaja.kasikortit.pop(int(indeksi))
            for i in range(len(lista)):
                pelaaja.kasikortit.append(self.pakka.nosta())
            break


    def panostuskierros(self):
        kierroksenAlussa = [p for p in self.pelaajat if p.aktiivinen == True]
        edelleenMukana = kierroksenAlussa.copy() #Tarvitaanko tätä mihinkään?!
        vuoro = self.jakaja
        
        while True:
            vuoro += 1 #Aloitetaan jakajasta seuraavasta, joten heti +1
            nytVuorossa = edelleenMukana[vuoro % len(kierroksenAlussa)]

            print("Vuoro", vuoro)
            valinnat = [p.valinta for p in edelleenMukana]
            print(edelleenMukana, "valinnat", valinnat)
            print("Eka ehto:", all(p.valinta in (1, 3) for p in edelleenMukana))
            print("Toka ehto:", sum(p.valinta == 2 for p in edelleenMukana) )
            
            if nytVuorossa.valinta == 3: #jos pelaaja on foldannut
                print(nytVuorossa, "on foldannut")
                continue
            elif (nytVuorossa.valinta == 2 and sum(p.valinta == 2 for p in edelleenMukana) == 1): # Jos pelaaja on viimeksi korottanut eikä kukaan ole sen jälkeen korottanut lisää, niin kierros päättyy
                print("Kierros päättyi!")
                all(p.nollaaPanos() for p in kierroksenAlussa) #Nollataan panostukseen liittyvät muuttujat
                break

            else:
                print(nytVuorossa, "siirtyy panosfunktioon tilassa", nytVuorossa.valinta)
                self.pyydaPanostus(nytVuorossa)
            
            #Jos kaikki joko call tai fold niin panostuskierros päättyy
            if all(p.valinta in (1, 3) for p in edelleenMukana): 
                print("Kierros päättyi!")
                all(p.nollaaPanos() for p in kierroksenAlussa) #Nollataan panostukseen liittyvät muuttujat
                break


    def pyydaPanostus(self, pelaaja):
        print("Maksettavaa:", self.suurinKorotus - pelaaja.maksettuPanostukseen)
        print("No mitäs tehdään, 1. Call/check, 2. Raise, 3. Fold ???\n")
        valinta = input("Päätä heti! : ")
        pelaaja.valinta = int(valinta)
        
        #Nämä ehkä pitää erottaa vielä omiksi funktioiksi tms, tai oma allin-funktio (joka luo myös uuden potin) jos chipit ei riitä
        if pelaaja.valinta == 1:
            pelaaja.chips -= (self.suurinKorotus - pelaaja.maksettuPanostukseen)
            pelaaja.maksettuPanostukseen = self.suurinKorotus
        elif pelaaja.valinta == 2:
            print("VALINTA 2 ja suurinkorotus:", self.suurinKorotus)
            self.suurinKorotus += 100 #Alkuun vakio testiin
            print("LISÄYKSEN JÄLKEEN", self.suurinKorotus)
            pelaaja.chips -= self.suurinKorotus
            pelaaja.maksettuPanostukseen = self.suurinKorotus
        else:
            #jotain jolla pelaaja muutetaan epäaktiivisesti ja poistetaan poteista
            print("foldasin ähähäh")

        
class Potti:
    def __init__(self, pelaajalista: list, alkupanos: int):
        self.summa: int = 0
        self.maksettava: int = 0
        self.pelaajat = pelaajalista
        for pelaaja in pelaajalista:
            pelaaja.chips -= alkupanos # if pelaaja.chips > alkupanos else joku sidepotti
            self.summa += alkupanos

    #Kontribuutioista saadaan lopuksi luonnollisesti pottien summat laskettua
    #Kun pottien ei tarvitse tietää kuka maksoi paljonkin, lasketaan lopussa
    #vaan mukana olevien pelaajien maksamista summista erotukset (jos pienempi voittaa)






