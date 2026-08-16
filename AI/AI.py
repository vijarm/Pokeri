from Pistelasku import laskeArvot
from random import randint, sample
from Pakka import Pakka

class AI:
    def __init__(self, pelaaja):
        self.tyyppi = "Default"
        self.pelaaja = pelaaja

    def vaihdaKortit(self) -> list:
        NotImplemented
        return []  #Miten tää virhe oikeesti ohitellaan..

    def teePanostus(self):
        NotImplemented


class randomAI(AI):
    def vaihdaKortit(self) -> list:
        analysoitu = laskeArvot(self.pelaaja.nakyma.kasikortit, vaihtoja=True)
        vaihdettavat = []
        if len(analysoitu["vaihtosuositus"]) > 0:
            vaihtoIndex = randint(0, len(analysoitu["vaihtosuositus"]) - 1)  #Valinnaisesti yksi vaihtosuosituksista
            for kortti in analysoitu["vaihtosuositus"][vaihtoIndex]:
                vaihdettavat.append(kortti)
        return vaihdettavat

    def teePanostus(self):
        #Tähän jotain että 0,4 call 0,4 raise 0,2 fold ...
        pass


class montecarloAI(AI):

    def vaihdaKortit(self, maara: int = 100) -> list:
        analysoitu = laskeArvot(self.pelaaja.nakyma.kasikortit, vaihtoja=True)
        if len(analysoitu["vaihtosuositus"]) == 0:
            return []
        elif len(analysoitu["vaihtosuositus"]) == 1:
            return analysoitu["vaihtosuositus"][0]

        #print("--------- MONTE CARLO ----------")
        parasVaihto = -1
        parasVoima = -1
        for i in range(len(analysoitu["vaihtosuositus"])):
            tulos = self.testaaVaihto(self.pelaaja.kasikortit, analysoitu["vaihtosuositus"][i], maara)
            #print("VAIHTO PALAUTTI VOIMAN,", tulos, "VAIHTOON MENISI:", analysoitu["vaihtosuositus"][i])
            if tulos > parasVoima:
                parasVoima = tulos
                parasVaihto = i       

        #print("-- MONTE CARLO PERUSTEELLA VAIHTOON MENI:", analysoitu["vaihtosuositus"][parasVaihto], "--")  
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


class steadycarloAI(AI):

    def vaihdaKortit(self, maara: int = 100) -> list:
        analysoitu = laskeArvot(self.pelaaja.nakyma.kasikortit, vaihtoja=True)
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


class superAI(AI):
    pass

