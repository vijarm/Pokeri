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
# Palautetaan muodossa {"kasinimi": str, "vahvuus": tuple, "luokka": int}

from collections import Counter

def laskeArvot(kasikortit: list) -> dict:
    maat_counter = Counter(kortti.maa for kortti in kasikortit)
    numero_counter = Counter(kortti.numero for kortti in kasikortit)
    numero_arvot = sorted(numero_counter.values())

    suora = False
    vari = False
    vahvin = None
    vertailukortit = None
    luokka = None

# TÄSTÄ VOISI SIIRTÄÄ SUORAN JA VÄRIN TARKISTUKSEN SEN TAAKSE,
# ETTÄ ONKO KÄSI MUOTOA 1,1,1,1,1. Ei jaksa nyt. Koska etenkin suora tekee useemman toimen, ja on harvinainen.

    #Värin tarkistus
    if len(maat_counter) == 1:
        vari = True
    
    #Suoran tarkistus
    if len(numero_counter) == 5:
        jarjestetty = sorted(numero_counter)
        if jarjestetty[0] == 2 and jarjestetty[1] == 3 and jarjestetty[2] == 4 and jarjestetty[3] == 5 and jarjestetty[4] == 14:
            suora = True
            vertailukortit = 5
        else:
            laskuri = jarjestetty[0]
            suora = True
            for arvo in jarjestetty[1:]:
                if arvo == laskuri + 1:
                    laskuri = arvo
                else:
                    suora = False
                    break
            if suora: vertailukortit = laskuri
                
    #Värisuora
    if vari and suora:
        return {
            "kasinimi": "Värisuora", 
            "vahvuus": (8, vertailukortit), 
            "luokka": 20
            }    

    #Neloset                     
    elif numero_arvot == [1, 4]:
        for value, count in numero_counter.items():
            if count == 4:
                vahvin = value
            if count == 1:
                vertailukortit = value
        return {
            "kasinimi": "Neloset", 
            "vahvuus": (7, vahvin, vertailukortit), 
            "luokka": 19
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
            "luokka": 17
            }
    
    
    #Värin palautus arvojärjestyksessä
    elif vari:
        vertailukortit = sorted(numero_counter.keys(), reverse=True)
        return {
            "kasinimi": "Väri", 
            "vahvuus": (5, *vertailukortit), 
            "luokka": 15
            }
    
    #Suoran palautus arvojärjestyksessä
    elif suora: 
        return {
            "kasinimi": "Suora", 
            "vahvuus": (4, vertailukortit), 
            "luokka": 13
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
        return {
            "kasinimi": "Kolmoset", 
            "vahvuus": (3, vahvin, *vertailukortit), 
            "luokka": luokka
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
        return {
            "kasinimi": "Kaksi paria", 
            "vahvuus": (2, *vahvin, vertailukortit), 
            "luokka": luokka
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
        return {
            "kasinimi": "Pari", 
            "vahvuus": (1, vahvin, *vertailukortit), 
            "luokka": luokka
            }
    
    #Hai
    else:
        vertailukortit = sorted(numero_counter.keys(), reverse=True)
        luokka = 2 if vertailukortit[0] >= 13 else 1        
        return {
            "kasinimi": "Hai", 
            "vahvuus": (0, *vertailukortit), 
            "luokka": luokka
            }
    
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