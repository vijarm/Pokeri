from Pakka import Pakka, Kortti
from Pistelasku import laskeArvot, VOIMALUVUT
from Pelaaja import Pelaaja
from Pelipoyta import Pelipoyta
from Jako import Jako
from Panostus import PanostusKierros

#Kerää datan siitä, mitkä käsiluokat voittavat ja häviävät minkäkin verran, ja laskee keskimääräiset voimaluokat.
def tilastoiKadet(kierrosmaara: int, pelaajamaara: int, aiclass: str) -> list:  

    #Alustetaan pakka
    PerusPakka = Pakka()
    PerusPakka.luo_pakka()
    #Pelipakka kierrokselle on aina eri kuin PerusPakka
    PeliPakka = Pakka()
    PeliPakka.kortit = PerusPakka.kortit.copy()

    PeliPakka.sekoita()

    testilista = []
    for i in range(pelaajamaara):
        nimi = f"Pelaaja {i+1}"
        tyyppi = "Tietsikka"
        testilista.append(Pelaaja(nimi, tyyppi, AI_valinta=aiclass))

    testipeli = Pelipoyta(testilista)
    voittokadet = []
    haviajakadet = []
    niche = []  # Tallennetaan tilanteet joissa TODELLA VAHVA käsi on kuitenkin hävinnyt
    parhaathaviajat = [] # Häviävistä käsistä se, jolla on paras rank

    for i in range(0, 18):
        voittokadet.append(0)
        haviajakadet.append(0)
        parhaathaviajat.append(0)

    for _ in range(kierrosmaara):
        testipeli.jako = Jako(testipeli)

        testipeli.jako.jaaKortit()
        testipeli.paivitaNakymat()
        testipeli.jako.kerroKortit()

        for i in range(0, pelaajamaara):
            vaihtoja = testipeli.jako.pyydaVaihto(testipeli.jako.pelaajat[i])
            #print("Pelaaja", testipeli.jako.pelaajat[i].nimi, "vaihtoi", vaihtoja, "korttia.")

        voittaja = testipeli.jako.vertaaKadet(testipeli.jako.pelaajat)
        voittoluokka = voittaja[0]["voittoArvio"][0]
        voittokadet[voittoluokka] += 1

        for i in range(pelaajamaara):
            if testipeli.jako.pelaajat[i] != voittaja[0]["pelaaja"]:
                kasi = laskeArvot(testipeli.jako.pelaajat[i].kasikortit)
                if kasi["voittoArvio"][0] >= 16:
                    niche.append((kasi["kasikortit"], voittaja[0]["kasikortit"]))
                haviajakadet[kasi["voittoArvio"][0]] += 1

        #Parhaat häviäjät:
        ilmanvoittajaa = [p for p in testipeli.jako.pelaajat if p != voittaja[0]["pelaaja"]]
        parashaviaja = testipeli.jako.vertaaKadet(ilmanvoittajaa)
        luokka = parashaviaja[0]["voittoArvio"][0]
        parhaathaviajat[luokka] += 1

                
        testipeli.lopetaKierros()

    # Laskee keskiarvot voittajakäden voimalle ja parhaan häviäjän käden voimalle
    parashaviajaVoima = 0
    voittajaVoima = 0
    for i in range(len(voittokadet)):
        parashaviajaVoima += parhaathaviajat[i] * VOIMALUVUT[i][1]
        voittajaVoima += voittokadet[i] * VOIMALUVUT[i][1]
    parashaviajaVoima = parashaviajaVoima / kierrosmaara
    voittajaVoima = voittajaVoima / kierrosmaara

    for i in range(len(niche)):
        print("KÄSI HÄVISI:", niche[i][0], "KÄDELLE:", niche[i][1])
    print ("ANALYYSI")
    print ("")

    for i in range(len(voittokadet)):
        print ("Voittoluokka:", i, "|| voittoja:", voittokadet[i], "|| häviöjä:", haviajakadet[i], "|| esiintyminen:", voittokadet[i] + haviajakadet[i])

    print("")

    print ("Voittajat:")
    print (voittokadet)
    print ("")
    print ("Häviäjät")
    print (haviajakadet)
    print ("")
    print ("Paras häviävä käsi")
    print (parhaathaviajat)
    print ("")
    print ("Voittajakäden keskimääräinen voima:", voittajaVoima)
    print ("Parhaan häviävän käden keskimääräinen voima:", parashaviajaVoima)


    return [voittokadet, haviajakadet, parhaathaviajat]


def testaaPanostusta(kierrosmaara: int, pelaajamaara: int, aiclass: str, aisettings: dict):

    #Alustetaan pakka
    PerusPakka = Pakka()
    PerusPakka.luo_pakka()
    #Pelipakka kierrokselle on aina eri kuin PerusPakka
    PeliPakka = Pakka()
    PeliPakka.kortit = PerusPakka.kortit.copy()

    PeliPakka.sekoita()

    testilista = []
    for i in range(pelaajamaara):
        nimi = f"Pelaaja {i+1}"
        tyyppi = "Tietsikka"
        testilista.append(Pelaaja(nimi, tyyppi, AI_valinta=aiclass, AI_asetukset=aisettings))

    testipeli = Pelipoyta(testilista)
    testipeli.kierros += 1
    testipeli.paivitaPanos()

    valinnat = [0,0,0,0]

    for _ in range(kierrosmaara):
        for p in testipeli.pelaajat:
            p.chips = 10000
            p.nollaaPanos()
            p.nollaaKierros()
        testipeli.jako = Jako(testipeli)
        testipeli.jako.panostuskierros = PanostusKierros(testipeli.jako, testipeli)
        testipeli.jako.panostuskierros.suurinKorotus = 100  #Laitetaan sinne heti korotus, jotta ei voi check (fold muuttuu calliksi muuten)

        testipeli.jako.jaaKortit()
        testipeli.paivitaNakymat()
        testipeli.jako.kerroKortit()

        for i in range(0, pelaajamaara):
            testipeli.paivitaNakymat()
            testipeli.jako.panostuskierros.pyydaPanostus(testipeli.jako.pelaajat[i])
            testipeli.paivitaNakymat()
            print("Pelaaja", testipeli.jako.pelaajat[i].nimi, "valitsi", testipeli.jako.pelaajat[i].valinta, "panostuksessa.")

            valinnat[testipeli.jako.pelaajat[i].valinta - 1] += 1  #Lasketaan valinnan numerolla indeksiin countit (Huom valintanro > indeksi)

        testipeli.paivitaNakymat()
        testipeli.lopetaKierros()

    print("valinnat kaikkinensa:", valinnat)
    print("valintoja tehtiin yhteensä:", sum(valinnat))
    print("LOPPUI")


def tilastoiVoitot(pelimaara: int, pelaajat=None):

    if not pelaajat:
        asetukset = [{"aggressiivisuus": 1}, {"aggressiivisuus": 2}, {"aggressiivisuus": 3}, {"aggressiivisuus": 3}]
        ai_type = ["montecarlo", "montecarlo", "montecarlo", "random"]
        pelaajat = []
        for i in range(4):
            nimi = f"Tietokone {i+1}"
            pelaajat.append(Pelaaja(nimi, "Tietsikka", AI_valinta=ai_type[i], AI_asetukset=asetukset[i]))

    Voitot = {}
    for pelaaja in pelaajat:
        Voitot[pelaaja] = 0

    for _ in range(pelimaara):
        MyGame = Pelipoyta(pelaajat)
        voittaja = MyGame.autoPeli()  #Palauttaa pelin voittaneen Pelaaja-olion
        Voitot[voittaja] += 1
        for p in pelaajat:
            p.nollaaKokoPeli()

    for pelaaja, voitot in Voitot.items():
        print("PELAAJA:", pelaaja.nimi, "|| VOITOT:", voitot, "|| LISÄTIEDOT:", pelaaja.ai_tyyppi, pelaaja.ai.asetukset)



# listat = tilastoiKadet(50, 2, "random")
# listat = tilastoiKadet(50, 4, "montecarlo")
# listat = tilastoiKadet(50, 4, "steady")

#asetukset = {"aggressiivisuus": 1}
#testaaPanostusta(500, 4, "random", asetukset)  #Huom tämä pelaa sen kierroksen, joten kun tulee raiseja niin muiden mahdollisuus muuttuu
#testaaPanostusta(5, 4, "montecarlo", asetukset)  

asetukset = [{"aggressiivisuus": 1}, {"aggressiivisuus": 2}, {"aggressiivisuus": 3}, {"aggressiivisuus": 3}]
ai_type = ["montecarlo", "montecarlo", "montecarlo", "random"]
pelaajat = []
for i in range(4):
    nimi = f"Tietokone {i+1}"
    pelaajat.append(Pelaaja(nimi, "Tietsikka", AI_valinta=ai_type[i], AI_asetukset=asetukset[i]))

tilastoiVoitot(1000, pelaajat)