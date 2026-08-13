from Pistelasku import laskeArvot, haeVoittaja
from Pelaaja import Pelaaja

'''
Koodi voisi näyttää siistimmältä jos panostuskierroksen olisi siirtänyt kokonaan omaan classiin,
mutta toistaiseksi olkoon näin. 
'''
'''        aktiiviset = [p for p in self.pelaajat if p.aktiivinen and p.chips > 0]  #Vain aktiiviset pelaa, lisävarmistus chips > 0
        if len(aktiiviset) < 2: return

        jakaja = aktiiviset.index(self.paivitaJakaja())
        panos = 100 + (50 * ((self.kierros - 1) // 4))  #panos nousee 50% alkupanoksesta joka 4. kierros, voi myös muuttaa muuttujaksi

        self.jako = Jako(self.pelipakka, aktiiviset, panos, jakaja)  

        
        def __init__(self, pelipakka, pelaajalista: list, alkupanos: int, jakaja: int):
                self.pakka = pelipakka
                self.pelaajat = pelaajalista
                self.mukanaPotissa = pelaajalista.copy()
                self.potti = 0
                self.alkupanos = alkupanos
                self.jakaja = jakaja #Jakajan indeksi pelaajalistasta
                self.vuoro = pelaajalista[jakaja]
                self.pelivaihe = 0  # 1 = 1. panostus | 2 = vaihdot | 3 = 2. panostus | 4 = showdown
        
        '''

class Jako:
    def __init__(self, pelipoyta):
        self.pelipoyta = pelipoyta
        self.pakka = pelipoyta.pelipakka
        self.pelaajat = [p for p in pelipoyta.pelaajat if p.aktiivinen and p.chips > 0]
        self.mukanaPotissa = self.pelaajat.copy()
        self.potti = 0
        self.alkupanos = 100 + (50 * ((pelipoyta.kierros - 1) // 4))  #panos nousee 50% alkupanoksesta joka 4. kierros, voi myös muuttaa muuttujaksi
        self.jakaja = self.pelaajat.index(pelipoyta.paivitaJakaja()) #Jakajan indeksi pelaajalistasta
        self.vuoro = self.pelaajat[self.jakaja]
        self.pelivaihe = 0  # 1 = 1. panostus | 2 = vaihdot | 3 = 2. panostus | 4 = showdown

        self.discardPile = [] #tarvitaanko, vai popataanko vaan veks?
        self.suurinKorotus: int = 0 

        self.pakka.sekoita()

    def pelaaKierros(self) -> list:
        self.keraaAlkupanokset()            
        self.jaaKortit()

        #panostuskierros ennen vaihtoja
        self.pelivaihe = 1
        voittaja = self.panostuskierros()
        if voittaja:
            print("KAIKKI MUUT FOLDASI JA", voittaja.nimi, "voitti!")
            return [(haeVoittaja([voittaja]), self.potti)]  #Kierrätetään haeVoittaja -kautta, eli käsi evaluoidaan ja näytetään aina? Pitää palauttaa listana!

        #vaihdot, alkaa jakajasta seuraavasta:
        self.pelivaihe = 2
        for i in range(1, len(self.pelaajat) + 1):
            vuorossa = self.pelaajat[(i + self.jakaja) % len(self.pelaajat)]
            if vuorossa in self.mukanaPotissa:
                vuorossa.vaihtoja = self.pyydaVaihto(vuorossa)

        #panostuskierros vaihtojen jälkeen
        self.pelivaihe = 3
        voittaja = self.panostuskierros()
        if voittaja:
            print("KAIKKI MUUT FOLDASI JA", voittaja.nimi, "voitti!")
            return [(haeVoittaja([voittaja]), self.potti)]

        self.pelivaihe = 4
        self.kerroKortit()
        voittaja = self.vertaaKadet(self.mukanaPotissa) #vertaaKadet hakee voittajat niin, että katsoo myös sidepotit?
        voittajalista = self.jaaPotti()
        print("\nNO NYT on testattu voittajalistaa ja siihen tuli tämmöstä:", voittajalista)
        return (voittajalista)

    def autoKierros(self) -> list:
        self.keraaAlkupanokset()            
        self.jaaKortit()

        #Sitten kun voi automatisoida niin tähän väliin tulee:
        #panostuskierros 

        for i in range(1, len(self.pelaajat) + 1):
                    vuorossa = self.pelaajat[(i + self.jakaja) % len(self.pelaajat)]
                    if vuorossa in self.mukanaPotissa:
                        vuorossa.vaihtoja = self.pyydaVaihto(vuorossa)

        #Sitten kun voi automatisoida niin tähän väliin tulee:
        #panostuskierros                         
        
        self.kerroKortit()
        voittaja = self.vertaaKadet(self.mukanaPotissa)
        voittajalista = self.jaaPotti()
        print("")
        print("Voittaja:", voittaja)
        return (voittajalista)

    def keraaAlkupanokset(self): 
        for pelaaja in self.pelaajat:
            assert pelaaja.aktiivinen == True #Vain aktiiviset on mukana jakokierroksella
            if pelaaja.chips > self.alkupanos:
                pelaaja.chips -= self.alkupanos
                pelaaja.maksettuJakoon += self.alkupanos
                self.potti += self.alkupanos
            else:
                self.potti += pelaaja.chips
                pelaaja.maksettuJakoon += pelaaja.chips
                pelaaja.chips = 0
                pelaaja.allin = True


    def jaaKortit(self): 
        alkukadet = self.pakka.jaaKortit(len(self.pelaajat), 5)
        for i in range(len(alkukadet)):
            self.pelaajat[i].kasikortit = alkukadet[i]
    
    def kerroKortit(self):
        for pelaaja in self.pelaajat:
            print("Pelaaja:", pelaaja.nimi, "käsikortit: ", pelaaja.kasikortit)
        print ("Pakkaan jäi kortteja:", len(self.pakka.kortit))

    def vertaaKadetWanha(self): #Tää poistuu koska on sama kuin pistelasku haeVoittaja?
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
    
    def vertaaKadet(self, pelaajat: list) -> list:  #Tarvitaanko mihinkään tätä funktiota välissä?
        aktiiviset = []
        for pelaaja in pelaajat:
            if pelaaja.aktiivinen: 
                aktiiviset.append(pelaaja)
        return haeVoittaja(aktiiviset)

    def jaaPotti(self) -> list:
        pottiaJaljella = self.potti
        voittajat = []  #Tallennetaan tupleen ([lista voittajista], näiden voittajien voittama potti)
        i = 0  #tuplen indeksi
        while pottiaJaljella > 0:  #Kun potti on jaettu kokonaan niin potin jakaminen pysähtyy
            voittaja = haeVoittaja(self.mukanaPotissa)  #voittaja on aina lista, vaikka voittajia olisi vain yksi
            print("MILTÄ NÄYTTÄÄ NYT VOITTAJALISTA:", voittaja)
            for x in range(len(voittaja)):  #i:des voittajatuple, [0] on i:dennen tuplen voittajalista
                self.mukanaPotissa.remove(voittaja[x]["pelaaja"]) #x:s voittajatuple, [0] on x:nnen tuplen voittajalista, sen x:s voittaja
            voittajanPanostus = voittaja[0]["pelaaja"].maksettuJakoon
            tamaPotti = 0
            for y in range(len(self.pelaajat)):
                tamaPotti += min(voittajanPanostus, self.pelaajat[y].maksettuJakoon)  #Lisätään pottiin y pelaajan osuus
                self.pelaajat[y].maksettuJakoon -= min(voittajanPanostus, self.pelaajat[y].maksettuJakoon)  #Vähennetään voittoihin maksettu osuus pelaajan jäljellä olevista kontribuutioista loppupottiin
            pottiaJaljella -= tamaPotti  #Vähennetään osuus jäljellä olevasta potista
            voittajat.append((voittaja, tamaPotti))
            print("Tästä voittokierroksesta maksettiin sivupottia", tamaPotti, "ja jäljelle jäi pottiin", pottiaJaljella)
            i+=1     

        return voittajat

    def pyydaVaihto(self, pelaaja: Pelaaja): #TÄHÄN sitten jotain, valitaan hiirellä, palauta lista. Funktio palauttaa vaihtojen lkm?
        while True:
            print("Vuorossa", pelaaja.nimi, "|| käsikortit: ", pelaaja.kasikortit)
            analysoitu = laskeArvot(pelaaja.kasikortit, vaihtoja=True)
            print("Kädessä on:", analysoitu["kasinimi"], "|| Vaihtosuosituksia:", analysoitu["vaihtosuositus"])
            vaihdettu = 0

            if pelaaja.tyyppi == "Tietsikka":
                if len(analysoitu["vaihtosuositus"]) > 0:
                    for kortti in analysoitu["vaihtosuositus"][0]:
                        pelaaja.kasikortit.remove(kortti)
                        pelaaja.kasikortit.append(self.pakka.nosta())
                        vaihdettu += 1
                return vaihdettu
            
            vaihdetaan = input("Mitä vaihdetaan indeksillä?")
            if vaihdetaan.strip() == "": break

            if vaihdetaan.strip() == "a":
                if len(analysoitu["vaihtosuositus"]) > 0:
                    for kortti in analysoitu["vaihtosuositus"][0]:
                        pelaaja.kasikortit.remove(kortti)
                        pelaaja.kasikortit.append(self.pakka.nosta())
                        vaihdettu += 1
                return vaihdettu

            lista = vaihdetaan.split(" ")

            #Tässä tapahtuu nyt se vaihto (yksi kerrallaan)
            for indeksi in sorted(lista, reverse=True):
                pelaaja.kasikortit.pop(int(indeksi))
            for i in range(len(lista)):
                pelaaja.kasikortit.append(self.pakka.nosta())
                vaihdettu += 1
            return vaihdettu

    def panostuskierros(self) -> Pelaaja | None:
        if sum(not p.allin for p in self.mukanaPotissa) <= 1:  #All-in ei osallistu panostukseen, on jo all-in.
            return None  #Jos vain max 1 pelaaja olisi panostamassa, panostuskierrosta ei tapahdu. 

        vuoro = 1  #Aloitetaan jakajasta suoraavasta, joten aloitusvuoro on 1
        print("Panostuskierros alkaa! Vuoro on", vuoro, "ja jakajaindex pelillä on", self.jakaja)
        
        while True:
            nytVuorossa = self.pelaajat[(vuoro + self.jakaja) % len(self.pelaajat)] 
            self.vuoro = nytVuorossa
            print("Vuoro", vuoro, "pelaaja:", nytVuorossa.nimi)
            
            if nytVuorossa not in self.mukanaPotissa or nytVuorossa.allin == True: #jos pelaaja on foldannut tai mennyt all-in
                print(nytVuorossa, "on foldannut tai allin -> ohitetaan")
                if all(p.allin for p in self.mukanaPotissa): #Jos kaikki pelaajat on all-in, panostuskierros päättyy
                    break
                vuoro += 1
                continue
            #Jos pelaajan edellisen vuoron jälkeen ei ole tullut korotuksia && kierros on mennyt vähintään kerran ympäri -> kierros päättyy
            elif (nytVuorossa.maksettuPanostukseen == self.suurinKorotus and vuoro > len(self.pelaajat)): 
                break

            else:
                print(nytVuorossa, "siirtyy panosfunktioon tilassa", nytVuorossa.valinta)
                self.pyydaPanostus(nytVuorossa)
            
            vuoro += 1

        #Tarkistetaanko onko joku maksanut "liikaa" -> korotus johon kukaan ei ole vastannut palautetaan
        SuurinPanosEnsin = sorted(self.pelaajat, key=lambda p: p.maksettuPanostukseen, reverse=True)
        print("Suurimmat panokset: ", SuurinPanosEnsin)
        if len(SuurinPanosEnsin) >= 2:
            maksettuLiikaa = SuurinPanosEnsin[0].maksettuPanostukseen - SuurinPanosEnsin[1].maksettuPanostukseen
            if maksettuLiikaa != 0:
                print("PALAUTETAAN LIIKAA MAKSETTU PELAAJALLE,", SuurinPanosEnsin[0].nimi, "yhteensä:", maksettuLiikaa)
                self.potti -= maksettuLiikaa  #Vähennetään potista ja pelaajan kontribuutio-tiedoista, lisätään chipit stackiin.
                SuurinPanosEnsin[0].maksettuJakoon -= maksettuLiikaa
                SuurinPanosEnsin[0].maksettuPanostukseen -= maksettuLiikaa
                SuurinPanosEnsin[0].chips += maksettuLiikaa

        print("PANOSTUSKIERROS OHI JA POTISSA ON", self.potti)
        for p in self.pelaajat:
            print("Pelaaja:", p.nimi, "maksanut pottiin:", p.maksettuPanostukseen, "ja maksanut jakoon:", p.maksettuJakoon)
        
        for p in self.pelaajat: #Nollataan panostuskierroksen tiedot
            p.nollaaPanos()
        self.suurinKorotus = 0

        if len(self.mukanaPotissa) == 1: 
            return self.mukanaPotissa[0]
        else: 
            return None


    def pyydaPanostus(self, pelaaja: Pelaaja):
        maksettavaa = self.suurinKorotus - pelaaja.maksettuPanostukseen
        print("Maksettavaa:", maksettavaa, "|| Käsikortit:", pelaaja.kasikortit, "|| Potti:", self.potti)
        print("1. Check") if maksettavaa == 0 else print("1. Call")
        if (pelaaja.chips > maksettavaa): print("2. Raise") 
        print("3. Fold")

        try:
            valinta = int(input("Valintasi: "))
            if valinta not in (1,2,3):
                valinta = 1
        except ValueError:
            valinta = 1

        pelaaja.valinta = int(valinta)
        
        if pelaaja.valinta == 1:
            call = self.maksaPanos(pelaaja, maksettavaa)
            print("Pelaaja", pelaaja.nimi, "-> CALL", call, "merkkiä!")

        elif pelaaja.valinta == 2:
            korotus = self.maksaPanos(pelaaja, maksettavaa + self.alkupanos)
            print("Pelaaja", pelaaja.nimi, "-> KOROTUS", korotus, "merkkiä!")

        else:
            if maksettavaa > 0:
                self.mukanaPotissa.remove(pelaaja)
                print("Pelaaja", pelaaja.nimi, "-> FOLD")
                pelaaja.valinta = 3 #Tämä vain siksi, että funktio ei nyt tarkista syötettä, ja voi jäädä loop jos syöttää 4 tms
            else: 
                pelaaja.valinta = 1 #automaattinen check, ei voi foldata ilman panosta vastassa.
                print("Pelaaja ei foldaa, koska ei ole maksettavaa, pakotettu CHECK!")


    def maksaPanos(self, pelaaja: Pelaaja, maara: int) -> int:
        if pelaaja.chips > maara:
            self.potti += maara
            pelaaja.maksettuPanostukseen += maara
            pelaaja.maksettuJakoon += maara
            pelaaja.chips -= maara
            if pelaaja.valinta == 2:
                self.suurinKorotus += self.alkupanos
        else: #Kun pelaajalla chipsejä vähemmän kuin pyydetty määrä, maksetaan kaikki mitä on, ja chips = 0.
            maara = pelaaja.chips
            self.potti += maara
            pelaaja.maksettuPanostukseen += maara
            pelaaja.maksettuJakoon += maara
            if pelaaja.valinta == 2 and pelaaja.maksettuPanostukseen > self.suurinKorotus:
                self.suurinKorotus = pelaaja.maksettuPanostukseen
            pelaaja.chips = 0
            pelaaja.allin = True
        print("\nTämä pelaaja on nyt maksanut panostukseen,", pelaaja.maksettuPanostukseen, "ja koko jakoon", pelaaja.maksettuJakoon, "\n")
        return maara #Palauttaa pottiin maksettujen chippien määrän



''' Tätä ei tarvita, jos seurataan intillä ja tehdään kuten alla mainittu        
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
'''





