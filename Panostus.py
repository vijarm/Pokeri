from Pelaaja import Pelaaja


class PanostusKierros:
    def __init__(self, jako, pelipoyta, kierros=2):
        self.jako = jako
        self.pelipoyta = pelipoyta

        self.kierros = kierros # kierros 1 = ennen vaihtoja, 2 = vaihtojen jälkeen
        self.panos = jako.panos
        self.pelaajaVuorossa = jako.pelaajat[jako.jakaja]

        self.suurinKorotus: int = 0 

        self.vuoro = 1
        self.valmis = False
        self.odottaaValintaa = False
        self.panostusValinta = None
        self.voittaja = None
        self.fold_voitto = False

    #Panostuskierroksen päälooppi
    def paivitaTila(self):

        if self.valmis:
            return

        if self.fold_voitto:
            #ihmispelaaja = next(p for p in self.pelipoyta.pelaajat if not p.ai)  #Host? Yhteinen ok?
            if self.pelipoyta.simulointi is False:
                if self.pelipoyta.ok is False:
                    return

            self.fold_voitto = False
            self.valmis = True
            self.odottaaValintaa = False
            self.pelipoyta.ok = False
            return

        if self.odottaaValintaa:
            if self.panostusValinta is None:
                return

            if self.panostusValinta == "maksa": valinta = 1
            elif self.panostusValinta == "pieniKorotus": valinta = 2
            elif self.panostusValinta == "suuriKorotus": valinta = 3
            elif self.panostusValinta == "luovuta": valinta = 4
            else: raise ValueError("Tuntematon panostuksen valintateksti:", self.panostusValinta)

            self.vastaanotaPanostus(self.pelaajaVuorossa, valinta)
            self.panostusValinta = None
            return            

        if sum(not p.allin for p in self.jako.mukanaPotissa) <= 1:  #All-in ei osallistu panostukseen
            self.lopetaKierros()  #Jos max 1 pelaaja olisi panostamassa, panostuskierrosta ei tarvita. 
            return  
        
        self.pelipoyta.paivitaNakymat()
                
        while True:
            self.pelaajaVuorossa = self.jako.pelaajat[(self.vuoro + self.jako.jakaja) % len(self.jako.pelaajat)] 
            
            if self.pelaajaVuorossa not in self.jako.mukanaPotissa or self.pelaajaVuorossa.allin == True: #jos pelaaja on foldannut tai mennyt all-in
                if all(p.allin for p in self.jako.mukanaPotissa): #Jos kaikki pelaajat on all-in, panostuskierros päättyy
                    self.lopetaKierros()
                    return
                self.vuoro += 1
                continue
            #Jos pelaajan edellisen vuoron jälkeen ei ole tullut korotuksia && kierros on mennyt vähintään kerran ympäri -> kierros päättyy
            if (self.pelaajaVuorossa.maksettuPanostukseen == self.suurinKorotus and self.vuoro > len(self.jako.pelaajat)): 
                self.lopetaKierros()
                return

            if self.pelaajaVuorossa.ai is not None:  #AI voi jatkaa suoraan
                valinta = self.pelaajaVuorossa.pyydaPanostus(self.kierros)
                self.kasittelePanostus(self.pelaajaVuorossa, valinta)
                self.vuoro += 1
                self.pelipoyta.paivitaNakymat()
                continue

            else:
                #Ihmispelaaja jää odottamaan valintaa
                self.odottaaValintaa = True
                self.pelipoyta.paivitaNakymat()
                self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "pyydaPanos", "pelaaja": self.pelaajaVuorossa.nimi})
                return

    '''
    def suoritaKierros(self) -> Pelaaja | None:
        if sum(not p.allin for p in self.jako.mukanaPotissa) <= 1:  #All-in ei osallistu panostukseen, on jo all-in.
            return None  #Jos vain max 1 pelaaja olisi panostamassa, panostuskierrosta ei tapahdu. 

        vuoro = 1  #Aloitetaan jakajasta suoraavasta, joten aloitusvuoro on 1
        print("Panostuskierros alkaa! Vuoro on", vuoro, "ja jakajaindex pelillä on", self.jako.jakaja)
        self.pelipoyta.paivitaNakymat()
        
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
    '''

    def kasittelePanostus(self, pelaaja: Pelaaja, valinta):

        maksettavaa = self.suurinKorotus - pelaaja.maksettuPanostukseen

        pelaaja.valinta = valinta
        ilmoitusteksti = None
        
        if valinta == 1:
            call = self.maksaPanos(pelaaja, maksettavaa)
            if call == 0:
                self.pelipoyta.loggaa(f"{pelaaja.nimi} check.")
                ilmoitusteksti = "Check!"
            else:    
                self.pelipoyta.loggaa(f"{pelaaja.nimi} maksoi {call} merkkiä.")
                ilmoitusteksti = f"Maksan {call}!"

        elif pelaaja.valinta == 2:
            korotus = self.maksaPanos(pelaaja, maksettavaa + self.panos)
            self.pelipoyta.loggaa(f"{pelaaja.nimi} maksoi {maksettavaa} ja korotti {korotus - maksettavaa} merkkiä.")
            ilmoitusteksti = f"Korotan {korotus - maksettavaa}!"

        elif pelaaja.valinta == 3:
            korotus = self.maksaPanos(pelaaja, maksettavaa + (3 * self.panos) )
            self.pelipoyta.loggaa(f"{pelaaja.nimi} maksoi {maksettavaa} ja korotti {korotus - maksettavaa} merkkiä.")
            ilmoitusteksti = f"Korotan {korotus - maksettavaa}!"

        else:
            if maksettavaa > 0:
                self.jako.mukanaPotissa.remove(pelaaja)
                self.pelipoyta.loggaa(f"{pelaaja.nimi} luovutti.")
                pelaaja.valinta = 4 
                pelaaja.folded = True
                ilmoitusteksti = "Luovutan!"
            else: 
                pelaaja.valinta = 1 #automaattinen check, ei voi foldata ilman panosta vastassa.
                self.pelipoyta.loggaa(f"{pelaaja.nimi} check.")
                ilmoitusteksti = "Check!"

        self.pelipoyta.paivitaNakymat()
        self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "panostus", "valinta": pelaaja.valinta, "pelaaja": pelaaja.nimi, "ilmoitus": ilmoitusteksti})
        self.odottaaValintaa = False


    def maksaPanos(self, pelaaja: Pelaaja, maara: int) -> int:  #Tätä varmaan voisi tiivistää/selkeyttää, mutta toimii
        if pelaaja.chips > maara:
            self.jako.potti += maara
            pelaaja.maksettuPanostukseen += maara
            pelaaja.maksettuJakoon += maara
            pelaaja.chips -= maara
            if pelaaja.valinta == 2 or pelaaja.valinta == 3:
                self.suurinKorotus = pelaaja.maksettuPanostukseen

        else: #Kun pelaajalla chipsejä vähemmän kuin pyydetty määrä, maksetaan kaikki mitä on, ja chips = 0.
            maara = pelaaja.chips
            self.jako.potti += maara
            pelaaja.maksettuPanostukseen += maara
            pelaaja.maksettuJakoon += maara
            if (pelaaja.valinta == 2 or pelaaja.valinta == 3) and pelaaja.maksettuPanostukseen > self.suurinKorotus:
                self.suurinKorotus = pelaaja.maksettuPanostukseen
            pelaaja.chips = 0
            pelaaja.allin = True
            self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "pelaajailmoitus", "pelaaja": pelaaja.nimi, "ilmoitus": "ALL-IN!"})


        print("\nTämä pelaaja on nyt maksanut panostukseen,", pelaaja.maksettuPanostukseen, "ja koko jakoon", pelaaja.maksettuJakoon, "\n")
        return maara #Palauttaa pottiin maksettujen chippien määrän


    def vastaanotaPanostus(self, pelaaja, valinta):
        assert pelaaja is not None

        self.kasittelePanostus(pelaaja, valinta)
        self.vuoro += 1

    def lopetaKierros(self):
        #Tarkistetaanko onko joku maksanut "liikaa" -> korotus johon kukaan ei ole vastannut palautetaan
        SuurinPanosEnsin = sorted(self.jako.pelaajat, key=lambda p: p.maksettuPanostukseen, reverse=True)

        if len(SuurinPanosEnsin) >= 2:
            maksettuLiikaa = SuurinPanosEnsin[0].maksettuPanostukseen - SuurinPanosEnsin[1].maksettuPanostukseen

            if maksettuLiikaa != 0:
                print("PALAUTETAAN LIIKAA MAKSETTU PELAAJALLE,", SuurinPanosEnsin[0].nimi, "yhteensä:", maksettuLiikaa)
                self.jako.potti -= maksettuLiikaa  #Vähennetään potista ja pelaajan kontribuutio-tiedoista, lisätään chipit stackiin.
                SuurinPanosEnsin[0].maksettuJakoon -= maksettuLiikaa
                SuurinPanosEnsin[0].maksettuPanostukseen -= maksettuLiikaa
                SuurinPanosEnsin[0].chips += maksettuLiikaa       
        
        for p in self.jako.pelaajat: #Nollataan panostuskierroksen tiedot
            p.nollaaPanos()
        self.suurinKorotus = 0

        if len(self.jako.mukanaPotissa) == 1: 
            self.voittaja = self.jako.mukanaPotissa[0]
            self.fold_voitto = True
            self.pelipoyta.loggaa(f"Muut foldasivat, {self.voittaja.nimi} voitti {self.jako.potti} merkkiä.")
            self.pelipoyta.paivitaNakymat()
            self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "fold_voitto", "showdownData": {"voittaja": self.voittaja.nimi, "potti": self.jako.potti}})

        else: 
            self.pelipoyta.loggaa(f"Panostuskierros päättyi, potissa: {self.jako.potti}") 
            self.pelipoyta.paivitaNakymat() 
            self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "yleisilmoitus", "ilmoitus": ["Panostuskierros päättynyt", f"Potissa {self.jako.potti} merkkiä"]})
            self.voittaja = None
            self.valmis = True
            self.odottaaValintaa = False



        

        


