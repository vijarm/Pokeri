from Pistelasku import laskeArvot
from random import randint, sample, choices, choice, random
from Pakka import Pakka
import pickle
import os


class AI:
    '''AI yleisluokka, funktioiden toteutus määritellään perityissä luokissa. 
    Saa parametreikseen pelaajan, jolle AI luodaan, sekä asetukset AI:n tarkemmasta tyypistä'''

    def __init__(self, pelaaja, asetukset: dict | None = None):  #aggro 1-3? type default / high hand / high card / safe?
        self.pelaaja = pelaaja

        if asetukset is None:
            self.asetukset = {}
        else: 
            self.asetukset = asetukset

        self.luokka = self.asetukset.get("luokka")  
        self.strategia = self.asetukset.get("strategia")
        self.aggressiivisuus = self.asetukset.get("aggressiivisuus", 2)  # 1 = passiivinen, 2 = normaali (default), 3 = aggro
        self.malli = self.asetukset.get("malli")
        
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

    def muokkaaPainotuksia(self, painot: list, kierros=1) -> list:  
        '''Useimmilla AI:lla käytössä oleva funktio, jolla muokataan panostuksen valintapainoja pelitilanteen mukaan sääntöpohjaisesti.'''

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
            uudetPainot[1] *= 2
            uudetPainot[2] *= 2

        if kierros == 1 and self.kasidata["voittoArvio"][0] > 4:  #Jos ennen vaihtoja kädessä on vähintään keskikokoinen pari, fold tn pienenee
            uudetPainot[3] *= 0.5

        if self.pelaaja.nakyma.potti / self.pelaaja.nakyma.chips > 0.5:  # Jos potissa on enemmän kuin puolet omista jäljellä olevista chipeistä, niin foldin todennäköisyys pienenee:
            uudetPainot[3] *= 0.7
            if self.pelaaja.nakyma.chips / self.pelaaja.nakyma.chips > 1:  # Ja jos potissa on enemmän kuin itsellä chippejä jäljellä, pienenee fold entisestään
                uudetPainot[3] *= 0.5
                if self.pelaaja.nakyma.chips / self.pelaaja.nakyma.chips > 3:  # Ja jos potti on suhteessa todella suuri
                    uudetPainot[3] *= 0.1

        #print("Maksettavaa:", maksettavaa, "|| Käsikortit:", self.pelaaja.nakyma.kasikortit, "|| Potti:", self.pelaaja.nakyma.potti)
        #print("Chips:", self.pelaaja.nakyma.chips, "|| Pieni raise:", pieniKorotus, "|| Suuri raise:", suuriKorotus)

        return uudetPainot



class randomAI(AI):
    '''Satunnainen AI-pelaaja. Ei täysin satunnainen, käyttää mm. ennalta määriteltyjä baseline -painoja, mutta sisältää
    muita enemmän satunnaisuutta, valitsee vaihdot suosituksista satunnaisesti.'''

    def vaihdaKortit(self) -> list:
        '''Palauttaa listana vaihdettavat kortit. Valitsee satunnaisesti vaihtosuosituksista.'''

        analysoitu = self.kasidata  #Tämä täytetään automaattisesti kun kortit jaetaan
        vaihdettavat = []
        if len(analysoitu["vaihtosuositus"]) > 0:
            if self.strategia == "Vahvat kädet":
                vaihdettavat = analysoitu["vaihtosuositus"][0]  #Listan ensimmäinen, ei optimi mutta esim. värin haku on listan alussa
            else:
                vaihtoIndex = randint(0, len(analysoitu["vaihtosuositus"]) - 1)  #Valinnaisesti yksi vaihtosuosituksista
                for kortti in analysoitu["vaihtosuositus"][vaihtoIndex]:
                    vaihdettavat.append(kortti)
        return vaihdettavat

    def pyydaPanostus(self, kierros=2) -> int:  #Random pelaaja tekee valintoja satunnaisesti, mutta kuitenkin noudattaen yksinkertaista logiikkaa painokertoimissa
        '''Palauttaa panostusvalinnan pohjautuen baseline-painotuksiin ja muokkaaPainotuksia -funktion toimintaan.'''

        vaihtoehdot = [1, 2, 3, 4]  # call, pieni korotus, suuri korotus, fold
        painot = PANOSTUS_TN[self.aggressiivisuus].copy()

        if not self.strategia == "taysirandom":  #taysirandom käyttää vain alustettuja peruslukuja
            painot = self.muokkaaPainotuksia(painot, kierros)  # AI:n yhteinen painotuksien muokkaus
        #print("todennäköisyyspainot valinnoille ovat:", painot)

        if self.strategia == "Deterministinen":
            valinta = vaihtoehdot[painot.index(max(painot))]
        else:
            valinta = choices(vaihtoehdot, painot, k=1)[0]

        #print("Valittiin", valinta)

        return valinta


class montecarloAI(AI):
    '''AI-pelaaja, joka käyttää vaihtojen tekemisessä apuna Monte Carlo -menetelmän kaltaista simulointia.'''

    def vaihdaKortit(self) -> list:  #Vaihdot päätetään normaalisti jo ennakkoon ensimmäisellä panostuskierroksella
        if self.vaihdetaan is not None:
            return self.vaihdetaan
        else:
            return self.haeParasVaihto()


    def haeParasVaihto(self, maara: int = 20) -> list:
        '''Tekee jokaiselle saadulle vaihtosuositukselle 20 vaihtoyritystä, laskee niistä keskimäärin parhaimman voimaluvun,
        ja valitsee sen mukaisen vaihdon.'''

        analysoitu = self.kasidata
        if self.asetukset is not None:
            maara = self.asetukset.get("MC_maara", 20)  # Vertailuvaihtoja otetaan 20kpl ellei AI-asetuksissa muuta määritetä.

        if len(analysoitu["vaihtosuositus"]) == 0:
            self.arvioituVoimakkuus = analysoitu["voittoArvio"][1]
            return []
        elif len(analysoitu["vaihtosuositus"]) == 1:
            self.arvioituVoimakkuus = self.testaaVaihto(self.pelaaja.nakyma.kasikortit, analysoitu["vaihtosuositus"][0], maara)
            #print("TEHTIIN MONTECARLO YHDELLÄ VAIHTOSUOSITUKSELLA JA ARVIOITU VOIMAKKUUS ON", self.arvioituVoimakkuus)
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
        #print("TEHTIIN MONTECARLO USEALLA VAIHTOSUOSITUKSELLA JA ARVIOITU VOIMAKKUUS ON", self.arvioituVoimakkuus)
        return analysoitu["vaihtosuositus"][parasVaihto]


    def testaaVaihto(self, kasikortit: list, vaihto: list, maara: int) -> float:
        '''Käy yksittäisen vaihdon kohdalla 20 (tai maara) yritystä läpi, laskee vaihtojen seurauksena saatujen käsien
        voimalukujen keskiarvon, ja palauttaa sen float:na.'''

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
            analysoituKasi = laskeArvot(uusiKasi)
            voima = (analysoituKasi)["voittoArvio"][1]

            if self.strategia == "Vahvat kädet":  #"Vahvojen käsien" hakemisella on suurempi todennäköisyys
                if analysoituKasi["voittoArvio"][0] >= 12:
                    voima *= 2.5

            summattuVoima += voima
        
        return summattuVoima / maara

    def pyydaPanostus(self, kierros=2) -> int:  
        '''Palauttaa AI:n panostusvalinnan. Jos kierros on ennen vaihtoja, käyttää hyödyksi arvioitua käden voimakkuutta,
        joka on laskettu 20 vaihtoyrityksen pohjalta. Valintojen todennäköisyyspainoja muokataan suhdeluvulla, joka
        lasketaan vertailemalla oman käden voimakkuutta keskimäärin voittoon tarvittavaan voimakkuutteen. Lisäksi painotuksia
        muokataan muokkaaPainotuksia -funktion avulla.
        Asetuksista riippuen lopullinen valinta on joko vaihtoehtojen välillä painotuksien mukaan satunnaisesti valittu,
        tai deterministisessä moodissa suurimman painon valinta.'''

        if kierros == 1:
            self.vaihdetaan = self.haeParasVaihto()  # Tämä päivittää myös self.arvioituVoimakkuus
            vertailuVoima = self.arvioituVoimakkuus
        else:
            self.kasidata = laskeArvot(self.pelaaja.nakyma.kasikortit)
            vertailuVoima = self.kasidata["voittoArvio"][1]

        pelaajia_alussa = sum(p.aktiivinen for p in self.pelaaja.nakyma.muutPelaajat) + 1
        pelaajia_jaljella = sum((p.aktiivinen and not p.folded) for p in self.pelaaja.nakyma.muutPelaajat) + 1

        assert vertailuVoima is not None
        suhdeluku = 0.5 * (vertailuVoima / PARASHAVIAJA[pelaajia_alussa]) + 0.5 * (vertailuVoima / PARASHAVIAJA[pelaajia_jaljella]) #Oman käden tai arvioidun käden suhdeluku keskimääräiseen parhaaseen häviävään käteen, painotuksen 0.5 alkuperäisen pelaajamäärän ja 0.5 vielä jäljellä olevan pelaajamäärän mukaan
        #print("Suhdeluku on:", suhdeluku)

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

        #print("todennäköisyyspainot valinnoille ovat:", painot)

        if self.strategia == "Deterministinen":
            raisetYhdessa = [painot[0], painot[1] + painot[2], painot[3]]  #Koska korotus on "jaettu" kahteen slottiin, niin yhdistetään niiden todennäköisyys
            alustavaValinta = raisetYhdessa.index(max(raisetYhdessa))
            if alustavaValinta == 0:
                valinta = vaihtoehdot[0]
            elif alustavaValinta == 2:
                valinta = vaihtoehdot[3]
            else:  #jos valinta on korotus, niin valitaan korotuksien välillä suuremman todennäköisyyden omaava
                valinta = vaihtoehdot[1] if painot[1] > painot[2] else vaihtoehdot[2]
        else:
            valinta = choices(vaihtoehdot, painot, k=1)[0]

        #print("Valittiin", valinta)

        return valinta


class steadycarloAI(AI):  #Ei käytössä toistaiseksi.. Ei eronnut tarpeeksi toisesta
    '''Ei käytössä toistaiseksi, mutta säilytetään. Tarkoituksena oli tehdä Monte Carlo pelaajaa vastaava
    pelaajamalli sillä erotuksella, että ensimmäinen pyrki hakemaan kättä, jolla saavuttaa kovimman voimaluvun,
    ja tämä taas hakisi kättä, joka keskimäärin useimmin riittää voittoon. Erot olivat kuitenkin testeissä liian pieniä.'''

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


#KOULUTUKESEN: Pelipoyta 123 - 143
#Panostus 75-85
#Muuten ton voisi laittaa PyydaPanostus alle?? Voisi koodata että nimi OPPIJA niin sillon menee koulutukseen?
class superAI(AI):
    '''Koneopetetun AI:n pelaajaluokka. Hyödyntää vaihdoissa Monte Carlon tapaan suosituksia, mutta panostusvalinnat
    tehdään vahvistusoppimisen keinoin opitulla tilannekuvalla. Käyttää Q-learning algoritmia, palkintona chippien muutos,
    ja palkinto jaetaan 0.8 kertoimella levittäen kaikille jaon aikana tapahtuneille päätöksille.'''

    def __init__(self, pelaaja, asetukset=None):  
        super().__init__(pelaaja, asetukset)

        self.q_table = {}
        self.koulutetut_jaot = 0

        self.learning_rate = 0.1  #Kuinka suuri muutos staten q-arvoihin
        self.epsilon = 1.0  #Kuinka usein käytetään satunnaista ratkaisua, 0 = aina max
        self.lambda_kerroin = 0.8  #Kuinka paljon vanhat päätökset taaksepäin vaikuttavat, 1 == kaikki yhtä tärkeitä

        self.action = [1,2,3,4]
        self.chips_jaon_alussa = None

        self.paatokset = []

        if self.malli is not None:
            self.lataa(KONEOPPIMIS_MALLIT[self.malli])


    def get_q_values(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0] * len(self.action)

        return self.q_table[state]

    def choose_action(self, state):
        '''Tekee panostusvalinnan perustuen opittuun Q-tableen ja parametrina saatuun pelitilanteeseen.'''

        q_values = self.get_q_values(state)

        if random() < self.epsilon:
            valinta = choice(self.action)

        else:
            paras_indeksi = q_values.index(max(q_values))
            valinta = self.action[paras_indeksi]

        return self.tarkistaLaillisuus(valinta)

    def update(self, state, action, reward):
        '''Päivittää Q-arvoa pelitilanteelle ja valinnalle algoritmin mukaan.'''

        q_values = self.get_q_values(state)
        current_q = q_values[action - 1]

        q_values[action - 1] += self.learning_rate * (reward - current_q)

    def tallenna(self, tiedosto=None):
        '''Tallentaa pickle-tiedostoon nykyisen Q-tablen arvot ja koulutukseen käytetyt parametrit.'''
        if tiedosto is None:
            tiedosto = self.malli

        if tiedosto is None:
            raise ValueError("Tallennustiedostoa ei ole määritetty")
        
        data = {
            "q_table": self.q_table,
            "epsilon": self.epsilon,
            "koulutetut_jaot": self.koulutetut_jaot,
            "learning_rate": self.learning_rate,
            "lambda_kerroin": self.lambda_kerroin
        }

        with open(tiedosto, "wb") as tiedosto_obj:
            pickle.dump(data, tiedosto_obj)

    def lataa(self, tiedosto="ai_data.pkl"):
        '''Lataa tiedostosta Q-tablen ja koulutukseen käytetyt parametrit.'''

        if not os.path.exists(tiedosto):
            return

        with open(tiedosto, "rb") as tiedosto_obj:
            data = pickle.load(tiedosto_obj)

        self.q_table = data["q_table"]
        self.epsilon = data["epsilon"]
        self.koulutetut_jaot = data["koulutetut_jaot"]
        self.learning_rate = data["learning_rate"]
        self.lambda_kerroin = data["lambda_kerroin"]

        print("AI ladattu:")
        print("Koulutettuja jakoja:", self.koulutetut_jaot)
        print("Epsilon:", self.epsilon)
        print("Q-table rivejä:", len(self.q_table))

        '''Latauksen yhteydessä jos haluaa tulostaa random esimerkin Q-arvosta:
        key = choice(list(self.q_table.keys()))
        print("Tila:", key)
        print("Q-arvot:", self.q_table[key])
        '''


    def tarkistaLaillisuus(self, valinta):
        '''Tarkistaa valitun toiminnan laillisuuden, ja tarvittaessa muokkaa sitä. Tällä hetkellä AI
        voi siis tehdä esim. pienen korotuksen valinnan vaikka suuri korotus olisi jo tehty, ja silloin
        funktio muokkaa sen lähimpään sopivaan valintaan,.'''

        maksettavaa = self.pelaaja.nakyma.suurinKorotus - self.pelaaja.nakyma.maksettuPanostukseen
        pieniKorotus = min(self.pelaaja.nakyma.panos, self.pelaaja.nakyma.chips - maksettavaa)
        suuriKorotus = min(3 * self.pelaaja.nakyma.panos, self.pelaaja.nakyma.chips - maksettavaa)

        suuriKorotusTehty = any(p.valinta == 3 for p in self.pelaaja.nakyma.muutPelaajat)
        pieniSallittu = pieniKorotus > 0 and not suuriKorotusTehty
        suuriSallittu = suuriKorotus > 0 and suuriKorotus > pieniKorotus

        if valinta == 4:  #Ei voi foldata jos ei ole mitään maksettavaa
            return 1 if maksettavaa == 0 else 4

        elif valinta == 3:

            if suuriSallittu:
                return 3

            else:  # Jos suuri korotus ei ole sallittu, mutta pieni on, palautetaan pieni korotus. Muuten call.
                if pieniSallittu:
                    return 2
                else:
                    return 1

        elif valinta == 2:

            if pieniSallittu:
                return 2

            else:  # Jos pieni korotus ei ole sallittu, mutta suuri on, palautetaan suuri korotus. Muuten call.
                if suuriSallittu:
                    return 3
                else:
                    return 1

        else:  #Call onnistuu aina
            return valinta
        

    def vaihdaKortit(self) -> list:  #Vaihdot päätetään normaalisti jo ennakkoon ensimmäisellä panostuskierroksella
        if self.vaihdetaan is not None:
            return self.vaihdetaan
        else:
            return self.haeParasVaihto()


    def haeParasVaihto(self, maara: int = 20) -> list:
        '''Tekee jokaiselle saadulle vaihtosuositukselle 20 vaihtoyritystä, laskee niistä keskimäärin parhaimman voimaluvun,
        ja valitsee sen mukaisen vaihdon.'''

        analysoitu = self.kasidata
        if self.asetukset is not None:
            maara = self.asetukset.get("MC_maara", 20)  # Vertailuvaihtoja otetaan 20kpl ellei AI-asetuksissa muuta määritetä.

        if len(analysoitu["vaihtosuositus"]) == 0:
            self.arvioituVoimakkuus = analysoitu["voittoArvio"][1]
            return []
        elif len(analysoitu["vaihtosuositus"]) == 1:
            self.arvioituVoimakkuus = self.testaaVaihto(self.pelaaja.nakyma.kasikortit, analysoitu["vaihtosuositus"][0], maara)
            #print("TEHTIIN MONTECARLO YHDELLÄ VAIHTOSUOSITUKSELLA JA ARVIOITU VOIMAKKUUS ON", self.arvioituVoimakkuus)
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
        #print("TEHTIIN MONTECARLO USEALLA VAIHTOSUOSITUKSELLA JA ARVIOITU VOIMAKKUUS ON", self.arvioituVoimakkuus)
        return analysoitu["vaihtosuositus"][parasVaihto]


    def testaaVaihto(self, kasikortit: list, vaihto: list, maara: int) -> float:
        '''Käy yksittäisen vaihdon kohdalla 20 (tai maara) yritystä läpi, laskee vaihtojen seurauksena saatujen käsien
        voimalukujen keskiarvon, ja palauttaa sen float:na.'''

        testiPakka = Pakka()
        testiPakka.luo_pakka()
        testiPakka.kortit = [k for k in testiPakka.kortit if k not in kasikortit]  # Pakka jossa on kaikki muut paitsi omat käsikortit
        testiPakka.sekoita()

        testikasi = [k for k in kasikortit if k not in vaihto]
        vaihtomaara = len(vaihto)
        summattuVoima = 0

        for _ in range(maara):
            uusiKasi = testikasi.copy()
            uusiKasi.extend(sample(testiPakka.kortit,vaihtomaara))
            analysoituKasi = laskeArvot(uusiKasi)
            voima = (analysoituKasi)["voittoArvio"][1]

            if self.strategia == "Vahvat kädet":  #"Vahvojen käsien" hakemisella on suurempi todennäköisyys
                if analysoituKasi["voittoArvio"][0] >= 12:
                    voima *= 2.5

            summattuVoima += voima
        
        return summattuVoima / maara



        
#Alla olevat luvut on vanhoilta malleilta, niitä voisi päivittää ja/tai lisätä turvamarginaalia
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
    1: [60, 15, 5, 20], 
    2: [50, 20, 10, 20],
    3: [35, 20, 20, 25]
}

KONEOPPIMIS_MALLIT = {
    "Koneoppinut": "models/ai_jatkuva.pkl",
    "Koneoppinut 500k": "models/ai_500k.pkl",
    "Koneoppinut 1M": "models/ai_1m.pkl",
    "Koneoppinut 2M": "models/ai_2m.pkl",
    "Koneoppinut 5M": "models/ai_5m.pkl"
}
