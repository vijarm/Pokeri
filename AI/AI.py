from Pistelasku import laskeArvot
from random import randint, sample, choices
from Pakka import Pakka

class AI:
    def __init__(self, pelaaja, asetukset: dict | None = None):  #aggro 1-3? type default / high hand / high card / safe?
        self.pelaaja = pelaaja

        if asetukset is None:
            self.asetukset = {}
        else: 
            self.asetukset = asetukset

        self.strategia = self.asetukset.get("strategia")
        self.aggressiivisuus = self.asetukset.get("aggressiivisuus", 2)  # 1 = passiivinen, 2 = normaali (default), 3 = aggro
        
        self.kasidata: dict  # Pistelaskun kautta analysoitu data tulee tähän.
        self.vaihdetaan: list | None = None  # Jos käsi analysoidaan jo panostuskierrokselle ennen vaihtoja, vaihdot tallennetaan valmiiksi muistiin
        self.arvioituVoimakkuus: float | None = None  # Kuinka vahvaksi käden arvioidaan tulevan suunniteltujen vaihtojen jälkeen

    def vaihdaKortit(self) -> list:
        raise NotImplementedError

    def pyydaPanostus(self, kierros=2) -> int:
        raise NotImplementedError

    def nollaaKierros(self):  #Vain kierroksen päätteeksi, ei panostuksen jälkeen.
        self.kasidata = {}
        self.vaihdetaan = None
        self.arvioituVoimakkuus = None

    def muokkaaPainotuksia(self, painot: list, kierros=1) -> list:  # Kaikille AI:lle yhteinen funktio, jolla muokataan panostuksen valintapainoja pelitilanteen mukaan.
        uudetPainot = painot
        maksettavaa = self.pelaaja.nakyma.suurinKorotus - self.pelaaja.nakyma.maksettuPanostukseen
        pieniKorotus = min(self.pelaaja.nakyma.panos, self.pelaaja.nakyma.chips - maksettavaa)
        suuriKorotus = min(3 * self.pelaaja.nakyma.panos, self.pelaaja.nakyma.chips - maksettavaa)

        if self.pelaaja.nakyma.valinta == 2 or self.pelaaja.nakyma.valinta == 3:  #Jos on itse viimeksi korottanut, lasketaan foldia
            uudetPainot[3] *= 0.5

        if maksettavaa >= 3 * self.pelaaja.nakyma.maksettuJakoon and self.kasidata["voittoArvio"][0] < 3:  #Jos tulee suuria korotuksia eikä omassa kädessä ole mitään, fold tn kasvaa
            uudetPainot[3] *= 2

        if not ((pieniKorotus > 0 and not any(p.valinta == 3 for p in self.pelaaja.nakyma.muutPelaajat))):  #jos pieni korotus ei mahdollinen
            uudetPainot[2] += (uudetPainot[1] * 0.8)  # Siirretään osa pienen korotuksen tn:stä suureen korotukseen
            uudetPainot[1] = 0

        if not (suuriKorotus > 0 and suuriKorotus > pieniKorotus):  #jos suuri korotus ei mahdollinen
            uudetPainot[2] = 0

        if self.kasidata["voittoArvio"][0] > 12:  #vahva käsi ei foldaa
            uudetPainot[3] = 0

        if maksettavaa == 0 and self.kasidata["voittoArvio"][0] > 5:  #Jos kukaan ei ole vielä korottanut ja kädessä vähintään suuri pari, korotus tn kasvaa
            uudetPainot[2] *= 1.2
            uudetPainot[3] *= 1.2

        if kierros == 2 and self.kasidata["voittoArvio"][0] < 4:  #Jos vaihtojen jälkeen käsi on heikko, foldin tn kasvaa
            uudetPainot[3] *= 1.5

        if kierros == 2 and self.kasidata["voittoArvio"][0] > 6:  #Jos vaihtojen jälkeen kädessä vähintään 2 paria, raise tn kasvaa
            uudetPainot[1] *= 1.5
            uudetPainot[2] *= 1.5

        if kierros == 1 and self.kasidata["voittoArvio"][0] > 4:  #Jos ennen vaihtoja kädessä on vähintään keskikokoinen pari, fold tn pienenee
            uudetPainot[3] *= 0.5

        if self.pelaaja.nakyma.potti / self.pelaaja.nakyma.chips > 0.5:  # Jos potissa on enemmän kuin puolet omista jäljellä olevista chipeistä, niin foldin todennäköisyys pienenee:
            uudetPainot[3] *= 0.7
            if self.pelaaja.nakyma.chips / self.pelaaja.nakyma.chips > 1:  # Ja jos potissa on enemmän kuin itsellä chippejä jäljellä, pienenee fold entisestään
                uudetPainot[3] *= 0.5
                if self.pelaaja.nakyma.chips / self.pelaaja.nakyma.chips > 3:  # Ja jos potti on suhteessa todella suuri
                    uudetPainot[3] *= 0.1

        print("Maksettavaa:", maksettavaa, "|| Käsikortit:", self.pelaaja.nakyma.kasikortit, "|| Potti:", self.pelaaja.nakyma.potti)
        print("Chips:", self.pelaaja.nakyma.chips, "|| Pieni raise:", pieniKorotus, "|| Suuri raise:", suuriKorotus)


        return uudetPainot



class randomAI(AI):
    def vaihdaKortit(self) -> list:
        analysoitu = self.kasidata  #Tämä täytetään automaattisesti kun kortit jaetaan
        vaihdettavat = []
        if len(analysoitu["vaihtosuositus"]) > 0:
            vaihtoIndex = randint(0, len(analysoitu["vaihtosuositus"]) - 1)  #Valinnaisesti yksi vaihtosuosituksista
            for kortti in analysoitu["vaihtosuositus"][vaihtoIndex]:
                vaihdettavat.append(kortti)
        return vaihdettavat

    def pyydaPanostus(self, kierros=2) -> int:  #Random pelaaja tekee valintoja satunnaisesti, mutta kuitenkin noudattaen yksinkertaista logiikkaa painokertoimissa

        vaihtoehdot = [1, 2, 3, 4]  # call, pieni korotus, suuri korotus, fold
        painot = PANOSTUS_TN[self.aggressiivisuus].copy()

        if not self.strategia == "taysirandom":  #taysirandom käyttää vain alustettuja peruslukuja
            painot = self.muokkaaPainotuksia(painot, kierros)  # AI:n yhteinen painotuksien muokkaus
        print("todennäköisyyspainot valinnoille ovat:", painot)
        valinta = choices(vaihtoehdot, painot, k=1)[0]

        print("Valittiin", valinta)

        return valinta


class montecarloAI(AI):

    def vaihdaKortit(self) -> list:  #Vaihdot päätetään normaalisti jo ennakkoon ensimmäisellä panostuskierroksella
        if self.vaihdetaan is not None:
            return self.vaihdetaan
        else:
            return self.haeParasVaihto()


    def haeParasVaihto(self, maara: int = 20) -> list:
        print("--------- MONTE CARLO ----------")
        analysoitu = self.kasidata
        if self.asetukset is not None:
            maara = self.asetukset.get("MC_maara", 20)  # Vertailuvaihtoja otetaan 20kpl ellei AI-asetuksissa muuta määritetä.

        if len(analysoitu["vaihtosuositus"]) == 0:
            self.arvioituVoimakkuus = analysoitu["voittoArvio"][1]
            return []
        elif len(analysoitu["vaihtosuositus"]) == 1:
            self.arvioituVoimakkuus = self.testaaVaihto(self.pelaaja.nakyma.kasikortit, analysoitu["vaihtosuositus"][0], maara)
            print("TEHTIIN MONTECARLO YHDELLÄ VAIHTOSUOSITUKSELLA JA ARVIOITU VOIMAKKUUS ON", self.arvioituVoimakkuus)
            return analysoitu["vaihtosuositus"][0]
    
        parasVaihto = -1
        parasVoima = -1
        # hae asetuksista maara jos siellä on
        for i in range(len(analysoitu["vaihtosuositus"])):
            tulos = self.testaaVaihto(self.pelaaja.nakyma.kasikortit, analysoitu["vaihtosuositus"][i], maara)
            #print("VAIHTO PALAUTTI VOIMAN,", tulos, "VAIHTOON MENISI:", analysoitu["vaihtosuositus"][i])
            if tulos > parasVoima:
                parasVoima = tulos
                parasVaihto = i       

        #print("-- MONTE CARLO PERUSTEELLA VAIHTOON MENI:", analysoitu["vaihtosuositus"][parasVaihto], "--")  
        self.arvioituVoimakkuus = parasVoima
        print("TEHTIIN MONTECARLO USEALLA VAIHTOSUOSITUKSELLA JA ARVIOITU VOIMAKKUUS ON", self.arvioituVoimakkuus)
        return analysoitu["vaihtosuositus"][parasVaihto]


    def testaaVaihto(self, kasikortit: list, vaihto: list, maara: int) -> float:
        testiPakka = Pakka()
        testiPakka.luo_pakka()
        testiPakka.kortit = [k for k in testiPakka.kortit if k not in kasikortit]  # Pakka jossa on kaikki muut paitsi omat käsikortit
        testiPakka.sekoita()
        #print("Pakkaan jäi kortteja,", len(testiPakka.kortit))
        #print(kasikortit)

        testikasi = [k for k in kasikortit if k not in vaihto]
        vaihtomaara = len(vaihto)
        summattuVoima = 0

        for _ in range(maara):
            uusiKasi = testikasi.copy()
            uusiKasi.extend(sample(testiPakka.kortit,vaihtomaara))
            summattuVoima += (laskeArvot(uusiKasi))["voittoArvio"][1]
        
        return summattuVoima / maara

    def pyydaPanostus(self, kierros=2) -> int:  #ainakin montecarlo ja superai haluaa tiedon onko 1. vai 2. vaihtokierros, käsi simulaatio valmiiks
        if kierros == 1:
            self.vaihdetaan = self.haeParasVaihto()  # Tämä päivittää myös self.arvioituVoimakkuus
            vertailuVoima = self.arvioituVoimakkuus
        else:
            self.kasidata = laskeArvot(self.pelaaja.nakyma.kasikortit)
            vertailuVoima = self.kasidata["voittoArvio"][1]

        pelaajia = sum(p.aktiivinen for p in self.pelaaja.nakyma.muutPelaajat) + 1

        assert vertailuVoima is not None
        suhdeluku = vertailuVoima / PARASHAVIAJA[pelaajia]  #Oman käden tai arvioidun käden suhdeluku keskimääräiseen parhaaseen häviävään käteen
        print("Suhdeluku on:", suhdeluku)

        if kierros == 2:  #toisella kierroksella lopullinen käsi on tiedossa, ja painoarvoja muokataan rajummin
            suhdeluku = suhdeluku ** 0.5  #kierroksella yksi suhdeluvun neliöjuuri

        vaihtoehdot = [1, 2, 3, 4]
        painot: list[float] = [x for x in PANOSTUS_TN[self.aggressiivisuus]]

        for i in range(len(painot)):  #Tässä muokataan valintojen painot suhdeluvun perusteella
            if i == 3:  #Foldin todennäköisyys jaetaan suhdeluvulla, muut kerrotaan. Min 0.3 huonoillakin käsillä
                painot[i] = painot[i] / max(suhdeluku, 0.3)
            else:
                painot[i] = painot[i] * max(suhdeluku, 0.3)

        painot = self.muokkaaPainotuksia(painot, kierros)  # AI:n yhteinen painotuksien muokkaus

        if kierros == 1 and vertailuVoima > 60:  #Jos ennen vaihtoa käsi on vahva, niin kasvaa raise tn:
            painot[1] *= 1.3
            painot[2] *= 1.3

        print("todennäköisyyspainot valinnoille ovat:", painot)
        valinta = choices(vaihtoehdot, painot, k=1)[0]
        print("Valittiin", valinta)    

        return valinta


class steadycarloAI(AI):

    def vaihdaKortit(self, maara: int = 100) -> list:
        analysoitu = self.kasidata
        if len(analysoitu["vaihtosuositus"]) == 0:
            return []
        elif len(analysoitu["vaihtosuositus"]) == 1:
            return analysoitu["vaihtosuositus"][0]

        # print("--------- STEADY CARLO ----------")
        parasVaihto = -1
        parasVoima = -1
        parasTulos = -1
        pelaajat = sum(p.aktiivinen for p in self.pelaaja.nakyma.muutPelaajat) + 1
        # print("Laskimme että aktiivisia pelaajia on ", pelaajat)
        for i in range(len(analysoitu["vaihtosuositus"])):
            tulos = self.testaaVaihto(self.pelaaja.kasikortit, analysoitu["vaihtosuositus"][i], maara, pelaajat)
            # print("VAIHTO PALAUTTI VOIMAN,", tulos, "VAIHTOON MENISI:", analysoitu["vaihtosuositus"][i])
            if tulos[0] > parasTulos:  # Jos voittaa enemmän käsiä vertailulukuun nähden
                parasTulos = tulos[0]
                parasVoima = tulos[1]
                parasVaihto = i       

            if tulos[0] == parasTulos:  # Jos tasan niin verrataan vielä voimalukuja
                if tulos[1] > parasVoima:
                    parasTulos = tulos[0]
                    parasVoima = tulos[1]
                    parasVaihto = i
                    

        # print("-- MONTE CARLO PERUSTEELLA VAIHTOON MENI:", analysoitu["vaihtosuositus"][parasVaihto], "--")  
        return analysoitu["vaihtosuositus"][parasVaihto]


    def testaaVaihto(self, kasikortit: list, vaihto: list, maara: int, pelaajia: int) -> tuple:
        testiPakka = Pakka()
        testiPakka.luo_pakka()
        testiPakka.kortit = [k for k in testiPakka.kortit if k not in kasikortit]  # Pakka jossa on kaikki muut paitsi omat käsikortit
        testiPakka.sekoita()
        # print(kasikortit)

        testikasi = [k for k in kasikortit if k not in vaihto]
        vaihtomaara = len(vaihto)
        voittavaKasi = 0
        summattuVoima = 0

        for _ in range(maara):
            uusiKasi = testikasi.copy()
            uusiKasi.extend(sample(testiPakka.kortit,vaihtomaara))
            analysoitu = laskeArvot(uusiKasi)
            summattuVoima += analysoitu["voittoArvio"][1]
            if analysoitu["voittoArvio"][1] > PARASHAVIAJA[pelaajia]:
                voittavaKasi += 1 
        
        return (voittavaKasi , summattuVoima / maara)

        
#ao luvut on randomilla, niitä voisi päivittää ja/tai lisätä turvamarginaalia
PARASHAVIAJANELIO = {  #Simuloinnin keskiarvorajat, minkä yli voimaluvun pitäisi olla, että voittaa käden eri pelaajamäärillä
    2: 8,
    3: 16,
    4: 24
}

PARASHAVIAJA = {  #Simuloinnin keskiarvorajat, minkä yli voimaluvun pitäisi olla, että voittaa käden eri pelaajamäärillä
    2: 18,
    3: 30,
    4: 40
}

PANOSTUS_TN = {  #Panostusvalintojen perustodennäköisyydet aggro: 1-3, valinta [call, pieni korotus, suuri korotus, fold]
    1: [50, 15, 5, 30], 
    2: [40, 20, 10, 30],
    3: [25, 20, 20, 35]
}


class superAI(AI):
    pass

#Entä semmonen type HUIJARI, joka vaihtaakin kortit x2

#Laitetaan suhdeluku niin että pelaajiaAlussa + pelaajiaNyt / 2 ? Niin kannustaa jatkamaan kun pelaajat vähenee
#Tai 0.7x nyt, 0.3x alussa