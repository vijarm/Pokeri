from Pakka import Pakka, Kortti
from Pistelasku import laskeArvot, VOIMALUVUT
from Pelaaja import Pelaaja
from Pelipoyta import Pelipoyta
from Jako import Jako

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


# listat = tilastoiKadet(1000, 2, "random")
listat = tilastoiKadet(50000, 4, "montecarlo")
# listat = tilastoiKadet(50000, 4, "steady")
