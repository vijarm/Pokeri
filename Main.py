from Pakka import Pakka, Kortti
from Pistelasku import laskeArvot
from Pelaaja import Pelaaja
from Pelipoyta import Pelipoyta


print("POKERIPELIN IHIMEELLINEN MUALIMA")

#Alustetaan pakka
PerusPakka = Pakka()
PerusPakka.luo_pakka()
#Pelipakka kierrokselle on aina eri kuin PerusPakka
PeliPakka = Pakka()
PeliPakka.kortit = PerusPakka.kortit.copy()


PeliPakka.sekoita()

for kortti in PeliPakka.kortit:
    Kortti.toString(self=kortti)

testilista = []
for i in range(4):
    if i < 2:
        nimi = f"Random {i+1}"
        tyyppi = "Tietsikka"
        AI_tyyppi = "random"
        testilista.append(Pelaaja(nimi, tyyppi, AI_valinta=AI_tyyppi))
    elif i == 2:
        nimi = f"Steadycarlo {i+1}"
        tyyppi = "Tietsikka"
        AI_tyyppi = "steady"
        testilista.append(Pelaaja(nimi, tyyppi, AI_valinta=AI_tyyppi))
    else:
        nimi = f"Montecarlo {i+1}"
        tyyppi = "Tietsikka"
        AI_tyyppi = "montecarlo"
        testilista.append(Pelaaja(nimi, tyyppi, AI_valinta=AI_tyyppi))




MyGame = Pelipoyta(testilista)

MyGame.autoPeli()  #pelaa tietokoneilla pelin kaikki kädet alusta loppuun

testilista = []
for i in range(4):
    nimi = f"Pelaaja {i+1}"
    tyyppi = "Ihminen"
    testilista.append(Pelaaja(nimi, tyyppi))

testilista[3].chips = 200

ManualGame = Pelipoyta(testilista)
# ManualGame.uusiKierros()  #Menee normimoodin mukaan yksi kierros, kaikki manual
# ManualGame.testiPeli()  #Täysi pelit chipit nolliin

'''Testijako
MyJako = Jako(PerusPakka, testilista, 0, 0)
MyJako.jaaKortit()
MyJako.kerroKortit()
MyJako.pelaajat[1].chips = 300
MyJako.pelaajat[2].chips = 250
MyJako.panostuskierros()
'''



'''
jako = Jako(PerusPakka, testilista)
jako.jaaKortit()
jako.kerroKortit()

kierroksia = 0


while True:
    Jako.nollaaKierros(jako)
    kierroksia = kierroksia + 1

    jako = Jako(PerusPakka, testilista)
    jako.jaaKortit()
#    kierros.kerroKortit()
    voittaja = jako.haeVoittaja()

    print("TÄÄLLÄ MAINISSA NYT VOITTAJA:", voittaja)

    if len(voittaja) > 1:
        print("EI menny ku", kierroksia, "kierrosta HAHAHA")
        break
'''


'''
laskuri = 0
while True:
    laskuri += 1
    kasi.clear()
    PeliPakka.kortit.clear()
    PeliPakka.kortit = PerusPakka.kortit.copy()
    PeliPakka.sekoita()
    kasikortit = Pakka.nosta_x(PeliPakka, 5)
    pisteet = laskePisteet(kasikortit)
    if pisteet[0] == "VÄRISUORA!":
        print("NYT LÖYTY:", pisteet[0])
        print("Meni", laskuri,  "kierrosta!")
        print(kasikortit)
        print("Primary: ", pisteet[1], "Secondary:", pisteet[2])
        break
'''

''' KOMMENTINGGGGG

kadet = PeliPakka.jaaKortit(3, 4)
print(kadet)

print("-----SIIVOTAAN PAKKA-----")
kadet.clear()
kasi.clear()
PeliPakka.kortit.clear()
PeliPakka.kortit = PerusPakka.kortit.copy()
PeliPakka.sekoita()
print(len(PeliPakka.kortit), " korttia")

kadet = PeliPakka.jaaKortit(3, 5)
print(kadet)



print("--------------------PELIKIERROS: ___---------")
kierros = Pelikierros(PerusPakka, 4)
kierros.jaaKortit()
kierros.kerroKortit()

print("--------------------PELIKIERROS NRO 2: ___---------")
kierros = Pelikierros(PerusPakka, 4)
kierros.jaaKortit()
kierros.kerroKortit()

'''
