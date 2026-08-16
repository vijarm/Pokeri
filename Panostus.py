from Pelaaja import Pelaaja


class PanostusKierros:
    def __init__(self, jako, pelipoyta):
        self.jako = jako
        self.pelipoyta = pelipoyta
        
        self.panos = jako.alkupanos
        self.pelaajaVuorossa = jako.pelaajat[jako.jakaja]

        self.suurinKorotus: int = 0 


    def suoritaKierros(self) -> Pelaaja | None:
        if sum(not p.allin for p in self.jako.mukanaPotissa) <= 1:  #All-in ei osallistu panostukseen, on jo all-in.
            return None  #Jos vain max 1 pelaaja olisi panostamassa, panostuskierrosta ei tapahdu. 

        vuoro = 1  #Aloitetaan jakajasta suoraavasta, joten aloitusvuoro on 1
        print("Panostuskierros alkaa! Vuoro on", vuoro, "ja jakajaindex pelillä on", self.jako.jakaja)
        
        while True:
            self.pelaajaVuorossa = self.jako.pelaajat[(vuoro + self.jako.jakaja) % len(self.jako.pelaajat)] 
            print("Vuoro", vuoro, "pelaaja:", self.pelaajaVuorossa.nimi)
            
            if self.pelaajaVuorossa not in self.jako.mukanaPotissa or self.pelaajaVuorossa.allin == True: #jos pelaaja on foldannut tai mennyt all-in
                print(self.pelaajaVuorossa, "on foldannut tai allin -> ohitetaan")
                if all(p.allin for p in self.jako.mukanaPotissa): #Jos kaikki pelaajat on all-in, panostuskierros päättyy
                    break
                vuoro += 1
                continue
            #Jos pelaajan edellisen vuoron jälkeen ei ole tullut korotuksia && kierros on mennyt vähintään kerran ympäri -> kierros päättyy
            elif (self.pelaajaVuorossa.maksettuPanostukseen == self.suurinKorotus and vuoro > len(self.jako.pelaajat)): 
                break

            else:
                print(self.pelaajaVuorossa, "siirtyy panosfunktioon tilassa", self.pelaajaVuorossa.valinta)
                self.pelipoyta.paivitaNakymat()  #Vuoro on siirtynyt ja löytynyt aktiivinen pelaaja, joka tekee vaihdot
                self.pyydaPanostus(self.pelaajaVuorossa)
            
            vuoro += 1

        #Tarkistetaanko onko joku maksanut "liikaa" -> korotus johon kukaan ei ole vastannut palautetaan
        SuurinPanosEnsin = sorted(self.jako.pelaajat, key=lambda p: p.maksettuPanostukseen, reverse=True)
        print("Suurimmat panokset: ", SuurinPanosEnsin)
        if len(SuurinPanosEnsin) >= 2:
            maksettuLiikaa = SuurinPanosEnsin[0].maksettuPanostukseen - SuurinPanosEnsin[1].maksettuPanostukseen
            if maksettuLiikaa != 0:
                print("PALAUTETAAN LIIKAA MAKSETTU PELAAJALLE,", SuurinPanosEnsin[0].nimi, "yhteensä:", maksettuLiikaa)
                self.jako.potti -= maksettuLiikaa  #Vähennetään potista ja pelaajan kontribuutio-tiedoista, lisätään chipit stackiin.
                SuurinPanosEnsin[0].maksettuJakoon -= maksettuLiikaa
                SuurinPanosEnsin[0].maksettuPanostukseen -= maksettuLiikaa
                SuurinPanosEnsin[0].chips += maksettuLiikaa

        print("PANOSTUSKIERROS OHI JA POTISSA ON", self.jako.potti)
        for p in self.jako.pelaajat:
            print("Pelaaja:", p.nimi, "maksanut pottiin:", p.maksettuPanostukseen, "ja maksanut jakoon:", p.maksettuJakoon)

        self.pelipoyta.paivitaNakymat() #Päivitetään näkymä ennen kuin kierros loppuu, joku pikku sleep?
        
        for p in self.jako.pelaajat: #Nollataan panostuskierroksen tiedot
            p.nollaaPanos()
        self.suurinKorotus = 0

        if len(self.jako.mukanaPotissa) == 1: 
            return self.jako.mukanaPotissa[0]
        else: 
            return None


    def pyydaPanostus(self, pelaaja: Pelaaja):

        maksettavaa = self.suurinKorotus - pelaaja.maksettuPanostukseen

        pelaaja.valinta = pelaaja.pyydaPanostus()
        
        if pelaaja.valinta == 1:
            call = self.maksaPanos(pelaaja, maksettavaa)
            print("Pelaaja", pelaaja.nimi, "-> CALL", call, "merkkiä!")

        elif pelaaja.valinta == 2:
            korotus = self.maksaPanos(pelaaja, maksettavaa + self.panos)
            print("Pelaaja", pelaaja.nimi, "-> KOROTUS", korotus, "merkkiä!")

        else:
            if maksettavaa > 0:
                self.jako.mukanaPotissa.remove(pelaaja)
                print("Pelaaja", pelaaja.nimi, "-> FOLD")
                pelaaja.valinta = 3 #Tämä vain siksi, että funktio ei nyt tarkista syötettä, ja voi jäädä loop jos syöttää 4 tms
            else: 
                pelaaja.valinta = 1 #automaattinen check, ei voi foldata ilman panosta vastassa.
                print("Pelaaja ei foldaa, koska ei ole maksettavaa, pakotettu CHECK!")


    def maksaPanos(self, pelaaja: Pelaaja, maara: int) -> int:
        if pelaaja.chips > maara:
            self.jako.potti += maara
            pelaaja.maksettuPanostukseen += maara
            pelaaja.maksettuJakoon += maara
            pelaaja.chips -= maara
            if pelaaja.valinta == 2:
                self.suurinKorotus += self.panos
        else: #Kun pelaajalla chipsejä vähemmän kuin pyydetty määrä, maksetaan kaikki mitä on, ja chips = 0.
            maara = pelaaja.chips
            self.jako.potti += maara
            pelaaja.maksettuPanostukseen += maara
            pelaaja.maksettuJakoon += maara
            if pelaaja.valinta == 2 and pelaaja.maksettuPanostukseen > self.suurinKorotus:
                self.suurinKorotus = pelaaja.maksettuPanostukseen
            pelaaja.chips = 0
            pelaaja.allin = True
        print("\nTämä pelaaja on nyt maksanut panostukseen,", pelaaja.maksettuPanostukseen, "ja koko jakoon", pelaaja.maksettuJakoon, "\n")
        return maara #Palauttaa pottiin maksettujen chippien määrän


