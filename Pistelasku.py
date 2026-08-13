# Lasketaan käsille vertailukelpoiset arvot sekä luokitellaan vahvinkoreihin tietokonepelaajaa varten
# Palauttaa tuplessa vertailukelpoisen arvon, jossa ensimmäinen numero käden perusarvo (alla) ja sen jälkeen tasapelitilanteessa tarvittavat arvot vertailukelpoisessa järjestyksessä
# Käsien rankit:
# 0 - Hai
# 1 - Pari
# 2 - Kaksi paria
# 3 - Kolmoset
# 4 - Suora
# 5 - Väri
# 6 - Täyskäsi
# 7 - Neloset
# 8 - Värisuora
#
# Palautetaan muodossa {"kasinimi": str, "vahvuus": tuple, "luokka": int, "vaihtosuositus": list}

from collections import Counter

def laskeArvot(kasikortit: list, vaihtoja = False) -> dict:
    maat_counter = Counter(kortti.maa for kortti in kasikortit)
    numero_counter = Counter(kortti.numero for kortti in kasikortit)
    numero_arvot = sorted(numero_counter.values())

    suora = False
    vari = False
    vahvin = None
    vertailukortit = None
    luokka = None
    vaihtosuositus = []  #lista listoista: voi olla useampia eri usean kortin vaihtosuosituksia

# TÄSTÄ VOISI SIIRTÄÄ SUORAN JA VÄRIN TARKISTUKSEN SEN TAAKSE,
# ETTÄ ONKO KÄSI MUOTOA 1,1,1,1,1. Ei jaksa nyt. Koska etenkin suora tekee useemman toimen, ja on harvinainen.

    #Värin tarkistus
    if len(maat_counter) == 1:
        vari = True

    if vaihtoja:  #Jos väri on yhtä vaille tosi, niin suositellaan vaihtoihin poikkeavaa korttia
        if len(maat_counter) == 2:  
            poikkeavaMaa = next((maa for maa, maara in maat_counter.items() if maara == 1), None)  #Jos toista löytyy 1, on toista oltava 4
            if poikkeavaMaa:
                vaihtosuositus.append([next(k for k in kasikortit if k.maa == poikkeavaMaa)])
    
    #Suoran tarkistus
    if len(numero_counter) == 5:
        jarjestetty = sorted(numero_counter)
        if jarjestetty[0] == 2 and jarjestetty[1] == 3 and jarjestetty[2] == 4 and jarjestetty[3] == 5 and jarjestetty[4] == 14:
            suora = True
            vertailukortit = 5  #vertailukortti suorassa on suurin kortti

        else:
            if all(jarjestetty[i] + 1 == jarjestetty[i+1] for i in range(4)):
                suora = True
                vertailukortit = jarjestetty[4]

        if vaihtoja and not suora:
            vaihdettava = suoraPaadytAuki(jarjestetty, kasikortit)
            if vaihdettava:
                vaihtosuositus.append(vaihdettava)         
                
    #Värisuora
    if vari and suora:
        return {
            "kasinimi": "Värisuora", 
            "vahvuus": (8, vertailukortit), 
            "luokka": 20,
            "vaihtosuositus": vaihtosuositus
            }    

    #Neloset                     
    elif numero_arvot == [1, 4]:
        for value, count in numero_counter.items():
            if count == 4:
                vahvin = value
            if count == 1:
                vertailukortit = value
                if vaihtoja:  #Vaikka nelosilla vaihto ei paranna voittomahdollisuuksia, niin se on pelillisesti järkevämpää kuin skipata
                    vaihtosuositus.append([next(k for k in kasikortit if k.numero == value)])

        return {
            "kasinimi": "Neloset", 
            "vahvuus": (7, vahvin, vertailukortit), 
            "luokka": 19,
            "vaihtosuositus": vaihtosuositus
            }

        
    #Täyskäsi
    elif numero_arvot == [2, 3]:
        for value, count in numero_counter.items():
            if count == 3:
                vahvin = value
            if count == 2:
                vertailukortit = value
        return {
            "kasinimi": "Täyskäsi", 
            "vahvuus": (6, vahvin, vertailukortit), 
            "luokka": 17,
            "vaihtosuositus": vaihtosuositus
            }
    
    
    #Värin palautus käsien arvojärjestyksessä
    elif vari:
        vertailukortit = sorted(numero_counter.keys(), reverse=True)
        return {
            "kasinimi": "Väri", 
            "vahvuus": (5, *vertailukortit), 
            "luokka": 15,
            "vaihtosuositus": vaihtosuositus
            }

    
    #Suoran palautus käsien arvojärjestyksessä
    elif suora: 
        return {
            "kasinimi": "Suora", 
            "vahvuus": (4, vertailukortit), 
            "luokka": 13,
            "vaihtosuositus": vaihtosuositus
            }
    
    
    #Kolmoset
    elif numero_arvot == [1, 1, 3]: #Kolmoset
        vertailukortit = []
        for value, count in numero_counter.items():
            if count == 3:
                vahvin = value
                luokka = 12 if (vahvin > 9) else 11
            if count == 1:
                vertailukortit.append(value)
        vertailukortit.sort(reverse=True)

        if vaihtoja:
            yksittaiset = [k for k in kasikortit if k.numero in vertailukortit]
            vaihtosuositus.append(yksittaiset)
            
        return {
            "kasinimi": "Kolmoset", 
            "vahvuus": (3, vahvin, *vertailukortit), 
            "luokka": luokka,
            "vaihtosuositus": vaihtosuositus
            }
    
    #Kaksi paria
    elif numero_arvot == [1, 2, 2]: #Kaksi paria
        vahvin = []
        for value, count in numero_counter.items():
            if count == 2:
                vahvin.append(value)
                vahvin.sort(reverse=True)
                if vahvin[0] >= 12: luokka = 9
                elif (vahvin[0] > 8 and vahvin[0] < 12): luokka = 8 
                else: luokka = 7
            if count == 1:
                vertailukortit = value
                if vaihtoja:
                    vaihtosuositus.append([next(k for k in kasikortit if k.numero == value)])  #Yksi suositus vaihtaa ylimääräinen kortti

        if vaihtoja:  #Toinen suositus vaihtaa ylimääräinen kortti + pienempi pari
            vaihdettavat = [k for k in kasikortit if k.numero == vertailukortit or k.numero == vahvin[1]]
            vaihtosuositus.append(vaihdettavat)
            
        return {
            "kasinimi": "Kaksi paria", 
            "vahvuus": (2, *vahvin, vertailukortit), 
            "luokka": luokka,
            "vaihtosuositus": vaihtosuositus
            }

    #Pari
    elif numero_arvot == [1, 1, 1, 2]: #Pari
        vertailukortit = []
        for value, count in numero_counter.items():
            if count == 2:
                vahvin = value
                if vahvin > 12: luokka = 5
                elif (vahvin > 9 and vahvin <= 12): luokka = 4
                else: luokka = 3
                
            if count == 1:
                vertailukortit.append(value)
        vertailukortit.sort(reverse=True)

        if vaihtoja:
            vaihdettavat = suoraPaadytAuki(numero_arvot, kasikortit)  #Vaihtoehto 1: yhden vaille suora (väri on lisätty jo alussa)
            if vaihdettavat:
                vaihtosuositus.append(vaihdettavat)

            vaihdettavat = [k for k in kasikortit if k.numero in vertailukortit]  #Vaihtoehto 2: vaihdetaan muut paitsi pari
            vaihtosuositus.append(vaihdettavat)

            if vahvin and vahvin < 7 and vertailukortit[0] >= 12:  #Vaihtoehto 3: jos pari on pieni "< 7" ja muissa iso kortti ">= 12" niin jätetään vain iso kortti
                vaihdettavat = [k for k in kasikortit if k.numero != vertailukortit[0]]
                vaihtosuositus.append(vaihdettavat)

            if vahvin and vahvin < 7 and vertailukortit[0] < 12:  #Vaihtoehto 4: jos pieni pari ja muista suurin "< 12" niin vaihdetaan kaikki
                vaihtosuositus.append(kasikortit)

        return {
            "kasinimi": "Pari", 
            "vahvuus": (1, vahvin, *vertailukortit), 
            "luokka": luokka,
            "vaihtosuositus": vaihtosuositus
            }
    
    #Hai
    else:
        vertailukortit = sorted(numero_counter.keys(), reverse=True)
        luokka = 2 if vertailukortit[0] >= 13 else 1   

        if vaihtoja:
            vaihdettavat = suoraPaadytAuki(numero_arvot, kasikortit)  #Vaihtoehto 1: yhden vaille suora (väri on lisätty jo alussa)
            if vaihdettavat:
                vaihtosuositus.append(vaihdettavat)

            if vertailukortit[0] >= 11:  #Vaihtoehto 2: jos kädessä kuvakortti (>= 11), vaihdetaan kaikki muut
                vaihdettavat = [k for k in kasikortit if k.numero != vertailukortit[0]]
                vaihtosuositus.append(vaihdettavat)

            vaihtosuositus.append(kasikortit)  #Vaihtoehto 3: vaihdetaan koko käsi
             
        return {
            "kasinimi": "Hai", 
            "vahvuus": (0, *vertailukortit), 
            "luokka": luokka,
            "vaihtosuositus": vaihtosuositus
            }

#Palauttaa listana kortin, jonka voi lisätä vaihtosuositus -listaan
#Haetaan vain päädyt auki olevan suoran mahdollisuutta, ei keskeltä avointa
def suoraPaadytAuki(numerolista: list, kasikortit: list) -> list | None:  
    jarjestetty = sorted(numerolista)
    
    if all(jarjestetty[i] + 1 == jarjestetty[i+1] for i in range(0,3)):
        return [next(k for k in kasikortit if k.numero == jarjestetty[4])]

    elif all(jarjestetty[i] + 1 == jarjestetty[i+1] for i in range(1,4)):
        return [next(k for k in kasikortit if k.numero == jarjestetty[0])]

    else:
        return None

    
'''
Tehdäänkö erilliset funktiot, joissa toinen hakee voittajan, palauttaa myös käden vahvuuden jne. 
Toinen analysoi myös suositukset vaihtoihin jne. Hakeeko yo funktio kuitenkin kaiken tiedon kerralla aina?
Joku flag haetaanko voittajaa vai analyysiä, ja sen perusteella palauttaa? 
'''
def haeVoittaja(pelaajat: list) -> list:
    tulos = []
    voittaja = []
    for pelaaja in pelaajat:
        pisteet = laskeArvot(pelaaja.kasikortit)
        pisteet["pelaaja"] = pelaaja
        tulos.append(pisteet)
        if len(voittaja) == 0 or voittaja[0]["vahvuus"] == pisteet["vahvuus"]: 
            voittaja.append(pisteet)
        else: 
            if voittaja[0]["vahvuus"] < pisteet["vahvuus"]:
                voittaja = [pisteet]
    tulos.sort(key=lambda p: p["vahvuus"], reverse=True)
    if len(voittaja) == 1:
        print ("VOITTAJA!!! Pelin voitti", voittaja[0]["pelaaja"], "kädessään", voittaja[0]["kasinimi"])
    else:
        print ("OHHHHOHHHHHHHHH TASAPELI!!! KATSOS:", voittaja)
    return voittaja    