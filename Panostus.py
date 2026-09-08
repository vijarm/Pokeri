from Pelaaja import Pelaaja


class PanostusKierros:
    '''Yksittäinen panostuskierros, jossa käydään läpi aktiivisien pelaajien valintoja (maksu, korotus, luovutus).
    Kierros päättyy, kun kierroksen aikana ei ole tullut uusia korotuksia, kun kaikki paitsi yksi pelaajaa on all-in,
    tai jos kaikki paitsi yksi pelaaja on luovuttanut.'''

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
        self.panostusValinta: str | None = None
        self.voittaja = None
        self.fold_voitto = False

    def paivitaTila(self):
        '''Päivittää panostuskierroksen tilaa, tarkistaa päättymisen ehdot.
        Muuttaa tilaksi fold_voitto, jos kaikki paitsi yksi pelaaja on luovuttanut.
        Tietokoneet tekevät päätökset välittömästi, ihmispelaajan kohdalla odotetaan GUI-valintaa.'''

        if self.valmis:
            return

        if self.vuoro == 1 and sum(not p.allin for p in self.jako.mukanaPotissa) <= 1:  #All-in ei osallistu panostukseen
            self.lopetaKierros()  #Jos max 1 pelaaja olisi panostamassa, panostuskierrosta ei tarvita. 
            return  

        if self.fold_voitto:
            if self.pelipoyta.simulointi is None:
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

                state = None  #Näitä state juttuja tarvitaan vain koulutusvaiheessa, valmiin voisi laittaa pyydaPanostus alle
                if self.pelaajaVuorossa.ai.luokka == "Koneoppinut":  
                    ai = self.pelaajaVuorossa.ai

                    if self.kierros == 1:  #Muut AI:t tekee nämä toimet panostusvalinnan yhteydessä, mutta koneoppinut ei (koulutusmoodissa)
                        ai.vaihdetaan = ai.haeParasVaihto()  # Tämä päivittää myös self.arvioituVoimakkuus

                    state = muodostaGameStateAI(self.pelaajaVuorossa, self.pelipoyta)

                    valinta = ai.choose_action(state)

                else:
                    valinta = self.pelaajaVuorossa.pyydaPanostus(self.kierros)

                self.kasittelePanostus(self.pelaajaVuorossa, valinta)

                if self.pelaajaVuorossa.ai.luokka == "Koneoppinut":
                    self.pelaajaVuorossa.ai.paatokset.append((state, self.pelaajaVuorossa.valinta))  #Valinta on voinut muuttua kasittelePanostuksen aikana, jos valinta ei ole ollut sallittu

                self.vuoro += 1
                self.pelipoyta.paivitaNakymat()
                continue

            else:
                #Ihmispelaaja jää odottamaan valintaa
                self.odottaaValintaa = True
                self.pelipoyta.paivitaNakymat()
                self.pelipoyta.paivitaGUI("pelipoyta", {"tapahtuma": "pyydaPanos", "pelaaja": self.pelaajaVuorossa.nimi})
                return



    def kasittelePanostus(self, pelaaja: Pelaaja, valinta):
        '''Käsittelee panostuksesta tehdyn valinnan. Varmistaa että valinta on sallittu, ja syöttää valinnan maksaPanos -funktiolle.'''

        maksettavaa = self.suurinKorotus - pelaaja.maksettuPanostukseen

        pelaaja.valinta = valinta
        if valinta not in (1,2,3,4):
            raise ValueError(f"Virheellinen panostusvalinta: {valinta}")

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
                if pelaaja in self.jako.mukanaPotissa:
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
        '''Käsittelee panostuksen maksamisen. Laskee lopullisen oikean summan niin, että pelaajan chipsit eivät voi mennä negatiiviseksi.
        Siirtää tarvittaessa pelaajan all-in tilaan. Lisää maksetut chipsit pottiin.'''

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

        #print("\nTämä pelaaja on nyt maksanut panostukseen,", pelaaja.maksettuPanostukseen, "ja koko jakoon", pelaaja.maksettuJakoon, "\n")
        return maara #Palauttaa pottiin maksettujen chippien määrän


    def vastaanotaPanostus(self, pelaaja, valinta):
        '''Siirtää GUI:sta tulleen panostusvalinnan maksettavaksi.'''
        assert pelaaja is not None

        self.kasittelePanostus(pelaaja, valinta)
        self.vuoro += 1

    def lopetaKierros(self):
        '''Päättää panostuskierroksen. Tarkistaa onko jokin pelaaja maksanut liikaa, ja palauttaa liikaa maksetun osuuden.
        Nollaa pelaajien panostuskierroksen tiedot. Jos pelaajia on jäljellä vain yksi, kirjaa siitä fold_voiton.'''

        #Tarkistetaanko onko joku maksanut "liikaa" -> korotus johon kukaan ei ole vastannut palautetaan
        SuurinPanosEnsin = sorted(self.jako.pelaajat, key=lambda p: p.maksettuPanostukseen, reverse=True)

        if len(SuurinPanosEnsin) >= 2:
            maksettuLiikaa = SuurinPanosEnsin[0].maksettuPanostukseen - SuurinPanosEnsin[1].maksettuPanostukseen

            if maksettuLiikaa != 0:
                #print("PALAUTETAAN LIIKAA MAKSETTU PELAAJALLE,", SuurinPanosEnsin[0].nimi, "yhteensä:", maksettuLiikaa)
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
            self.jako.fold_voitto = True
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

#Tämä olisi kuulunut tehdä yhteen pelaajanakyma -olion kanssa, eikä erillistä statea luotaisi.
def muodostaGameStateAI(pelaaja, pelipoyta):  
    '''Käytössä koneopetetulla AI:lla, luodaan gamestate johon perustuen AI tekee päätöksen.
    Asettaa tietyt arvot pooleihin, joilla rajataan gamestate -avaruuden laajuutta.'''

    assert pelaaja.ai is not None, "Funktio vain koneopetettavan AI:n käytössä"

    kasi_luokka = pelaaja.ai.kasidata["voittoArvio"][0]

    if pelipoyta.jako.panostuskierros.kierros == 1:
        if pelaaja.ai.arvioituVoimakkuus < 20:
            arvioitu_voimakkuus = 1
        elif pelaaja.ai.arvioituVoimakkuus < 30:
            arvioitu_voimakkuus = 2
        elif pelaaja.ai.arvioituVoimakkuus < 40:
            arvioitu_voimakkuus = 3
        elif pelaaja.ai.arvioituVoimakkuus < 60:
            arvioitu_voimakkuus = 4
        else:
            arvioitu_voimakkuus = 5
    else:
        arvioitu_voimakkuus = None

    kierros = 1 if pelipoyta.pelivaihe == 1 else 2
    pelaajia_alussa = len(pelipoyta.jako.pelaajat)
    pelaajia_jaljella = len([p for p in pelipoyta.jako.mukanaPotissa if not p.folded])

    pot_stack_suhde = pelipoyta.jako.potti / pelaaja.chips
    if pot_stack_suhde < 0.2:
        pot_stack_luokka = 1
    elif pot_stack_suhde < 0.5:
        pot_stack_luokka = 2
    elif pot_stack_suhde < 1:
        pot_stack_luokka = 3
    elif pot_stack_suhde < 2:
        pot_stack_luokka = 4
    else:
        pot_stack_luokka = 5
    
    stack_suhde = pelaaja.chips / 10000  
    if stack_suhde < 0.3:
        stack_luokka = 1
    elif stack_suhde < 0.7:
        stack_luokka = 2
    elif stack_suhde < 1.25:
        stack_luokka = 3
    elif stack_suhde < 1.75:
        stack_luokka = 4
    else:
        stack_luokka = 5

    vastustaja_raise = any(p.valinta in (2, 3) for p in pelipoyta.jako.mukanaPotissa if p is not pelaaja)
    oma_edellinen_valinta = pelaaja.valinta

    return (
        kasi_luokka,
        arvioitu_voimakkuus,
        kierros,
        pelaajia_alussa,
        pelaajia_jaljella,
        pot_stack_luokka,
        stack_luokka,
        vastustaja_raise,
        oma_edellinen_valinta
    )




        

        


