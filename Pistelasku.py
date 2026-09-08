from collections import Counter

def laskeArvot(kasikortit: list, vaihtoja = False) -> dict:
    '''Saa parametrikseen käsikortit -listan, josta tarkistetaan kyseisen käden pokerikäden vahvuus. 
    Vahvuus on vertailukelpoinen tuple, jossa ensimmäinen luku kuvaa kättä (esim. pari, kolmoset)
    ja seuraavat luvut muita tarkentavia tietoja (esim. mikä pari, ja seuraavaksi muut kortit suuruusjärjestyksessä).
    Näin yksinkertaisella suurempi kuin -vertailulla voidaan hakea paras käsi. 
    Lisäksi jos vaihtoja -parametri on True, lisätään suositukset korteista, joita kädestä voi olla järkevä vaihtaa.
    Lisäksi käsillä on vielä tarkempi 18-portainen luokittelu sekä voimaluku 0-100, joka lisätään analyysiin.
    
    Palauttaa:
    "kasinimi": Käden nimi (string)
    "vahvuus": Vertailukelpoinen tuple käden arvosta
    "voittoArvio": Tuple, ensimmäinen luku käden rank 0-17, toinen luku käden "voimaluku" 0-100
    "vaihtosuositus": Lista, jokainen alkio on yksi suositus vaihdettavista korteista
    '''

    maat_counter = Counter(kortti.maa for kortti in kasikortit)
    numero_counter = Counter(kortti.numero for kortti in kasikortit)
    numero_arvot = sorted(numero_counter.values())

    suora = False
    vari = False
    vahvin = None
    vertailukortit = None
    voittoArvio = None
    vaihtosuositus = []  #lista listoista: voi olla useampia eri usean kortin vaihtosuosituksia

# Tätä voisi saada optimoitua muuttamalla järjestystä, jossa vertailua tehdään - nyt edetään periaatteessa harvinaisimmasta yleisimpään

    #Värin tarkistus
    if len(maat_counter) == 1:
        vari = True

    if vaihtoja:  #Jos väri on yhtä vaille tosi, niin suositellaan vaihtoihin poikkeavaa korttia
        if len(maat_counter) == 2:  
            poikkeavaMaa = next((maa for maa, maara in maat_counter.items() if maara == 1), None)  #Jos toista löytyy 1, on toista oltava 4
            if poikkeavaMaa:
                vaihtosuositus.append([next(k for k in kasikortit if k.maa == poikkeavaMaa)])

        #Jos kolme samaa maata
        if sorted(maat_counter.values()) == [1,1,3] or sorted(maat_counter.values()) == [2,3]:
            kolmen_maa = next((maa for maa, maara in maat_counter.items() if maara ==3))
            vaihtosuositus.append([k for k in kasikortit if k.maa != kolmen_maa])
    
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
            "voittoArvio": VOIMALUVUT[17],
            "vaihtosuositus": vaihtosuositus,
            "kasikortit": kasikortit
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
            "voittoArvio": VOIMALUVUT[16],
            "vaihtosuositus": vaihtosuositus,
            "kasikortit": kasikortit
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
            "voittoArvio": VOIMALUVUT[15],
            "vaihtosuositus": vaihtosuositus,
            "kasikortit": kasikortit
            }
    
    
    #Värin palautus käsien arvojärjestyksessä
    elif vari:
        vertailukortit = sorted(numero_counter.keys(), reverse=True)
        return {
            "kasinimi": "Väri", 
            "vahvuus": (5, *vertailukortit), 
            "voittoArvio": VOIMALUVUT[14],
            "vaihtosuositus": vaihtosuositus,
            "kasikortit": kasikortit
            }

    
    #Suoran palautus käsien arvojärjestyksessä
    elif suora: 
        return {
            "kasinimi": "Suora", 
            "vahvuus": (4, vertailukortit), 
            "voittoArvio": VOIMALUVUT[13],
            "vaihtosuositus": vaihtosuositus
            }
    
    
    #Kolmoset
    elif numero_arvot == [1, 1, 3]: #Kolmoset
        vertailukortit = []
        for value, count in numero_counter.items():
            if count == 3:
                vahvin = value
                if (vahvin > 9):
                    voittoArvio = VOIMALUVUT[12]
                elif (vahvin > 5 and vahvin <= 9):
                    voittoArvio = VOIMALUVUT[11]
                else: voittoArvio = VOIMALUVUT[10]
            if count == 1:
                vertailukortit.append(value)
        vertailukortit.sort(reverse=True)

        if vaihtoja:
            yksittaiset = [k for k in kasikortit if k.numero in vertailukortit]
            yksittaiset.sort(key=lambda k: k.numero)
            vaihtosuositus.append(yksittaiset)  #Vaihdetaan molemmat 'ylimääräiset'
            vaihtosuositus.append([yksittaiset[0]])  #Vaihdetaan pienempi
            
        return {
            "kasinimi": "Kolmoset", 
            "vahvuus": (3, vahvin, *vertailukortit), 
            "voittoArvio": voittoArvio,
            "vaihtosuositus": vaihtosuositus
            }
    
    #Kaksi paria
    elif numero_arvot == [1, 2, 2]: #Kaksi paria
        vahvin = []
        for value, count in numero_counter.items():
            if count == 2:
                vahvin.append(value)
                vahvin.sort(reverse=True)
                if vahvin[0] >= 12: voittoArvio = VOIMALUVUT[9]
                elif (vahvin[0] > 7 and vahvin[0] < 12): voittoArvio = VOIMALUVUT[8] 
                else: voittoArvio = VOIMALUVUT[7]
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
            "voittoArvio": voittoArvio,
            "vaihtosuositus": vaihtosuositus
            }

    #Pari
    elif numero_arvot == [1, 1, 1, 2]: #Pari
        vertailukortit = []
        for value, count in numero_counter.items():
            if count == 2:
                vahvin = value
                if vahvin > 12: voittoArvio = VOIMALUVUT[6]
                elif (vahvin > 9 and vahvin <= 12): voittoArvio = VOIMALUVUT[5]
                elif (vahvin > 5 and vahvin <= 9): voittoArvio = VOIMALUVUT[4]
                else: voittoArvio = VOIMALUVUT[3]
                
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
            "voittoArvio": voittoArvio,
            "vaihtosuositus": vaihtosuositus
            }
    
    #Hai
    else:
        vertailukortit = sorted(numero_counter.keys(), reverse=True)
        if vertailukortit[0] >= 13:
            voittoArvio = VOIMALUVUT[2] 
        elif vertailukortit[0] > 9 and vertailukortit[0] < 13:
            voittoArvio = VOIMALUVUT[1] 
        else: voittoArvio = VOIMALUVUT[0]

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
            "voittoArvio": voittoArvio,  #kuvaa käsien välisiä vahvuuseroja (EI voittotodennäköisyys)
            "vaihtosuositus": vaihtosuositus
            }


def suoraPaadytAuki(numerolista: list, kasikortit: list) -> list | None:  
    '''Tarkistaa onko kädessä suoran haku ns. päädyt auki, eli neljä peräkkäistä korttia.
    Jos on, palauttaa vaihtosuosituksena eli listana sen kortin, joka ei kuulu neljän peräkkäisen kortin ryhmään.'''

    jarjestetty = sorted(numerolista)
    
    if all(jarjestetty[i] + 1 == jarjestetty[i+1] for i in range(0,3)):
        return [next(k for k in kasikortit if k.numero == jarjestetty[4])]

    elif all(jarjestetty[i] + 1 == jarjestetty[i+1] for i in range(1,4)):
        return [next(k for k in kasikortit if k.numero == jarjestetty[0])]

    else:
        return None

    
def haeVoittaja(pelaajat: list) -> list:
    '''Saa parametrina listan pelaajista. Vertaa kyseisten pelaajien käsikortit laskeArvot -funktiolla,
    ja palauttaa dict:nä tiedot voittokädestä sekä voittaneesta pelaajasta. 
    Voittaja palautetaan listana, koska tasapelitilanteessa voittajia on useampi.'''

    voittaja = []
    for pelaaja in pelaajat:
        pisteet = laskeArvot(pelaaja.kasikortit)
        pisteet["pelaaja"] = pelaaja  #Lisää tietoihin vielä Pelaaja -olion tiedon.
        if len(voittaja) == 0 or voittaja[0]["vahvuus"] == pisteet["vahvuus"]: 
            voittaja.append(pisteet)
        else: 
            if voittaja[0]["vahvuus"] < pisteet["vahvuus"]:
                voittaja = [pisteet]

    #if len(voittaja) == 1:
        #print ("VOITTAJA!!! Pelin voitti", voittaja[0]["pelaaja"], "kädessään", voittaja[0]["kasinimi"])
    #else:
        #print ("TASAPELI!!! Voittajat:", voittaja)
    
    return voittaja  #Tämä palautettava muoto ei nyt ehkä ole selkein... 



# Voimaluvut: (tunnus, vertailussa käytettävä vahvuusluku)
# Kun vahvuus >= 13, niin voittotodennäköisyys > 90
# Testattiin myös luvun neliöintiä, mutta nyt käytössä tavallinen muoto
# Voimaluvut on alunperin johdettu keräämällä statistiikkaa sadoista tuhansista pelatuista käsistä

VOIMALUVUT_NELIO = [
    (0, 0),    # Hai pieni
    (1, 0),    # Hai 9-12
    (2, 1),    # Hai >12
    (3, 2),    # Pari pieni
    (4, 5),    # Pari 6-9
    (5, 14),   # Pari 10-12
    (6, 31),   # Pari >12
    (7, 37),   # Kaksi paria, johtava <7
    (8, 43),   # Kaksi paria, johtava 7-11
    (9, 57),   # Kaksi paria, johtava >11
    (10, 64),  # Kolmoset pieni
    (11, 71),  # Kolmoset 6-9
    (12, 83),  # Kolmoset > 9
    (13, 91),  # Suora
    (14, 93),  # Väri 
    (15, 96),  # Täyskäsi
    (16, 99),  # Neloset
    (17, 100)  # Värisuora
]

VOIMALUVUT = [
    (0, 0),    # Hai pieni
    (1, 1),    # Hai 9-12
    (2, 6),    # Hai >12
    (3, 13),   # Pari pieni
    (4, 23),   # Pari 6-9
    (5, 38),   # Pari 10-12
    (6, 56),   # Pari >12
    (7, 61),   # Kaksi paria, johtava <7
    (8, 65),   # Kaksi paria, johtava 7-11
    (9, 75),   # Kaksi paria, johtava >11
    (10, 80),  # Kolmoset pieni
    (11, 84),  # Kolmoset 6-9
    (12, 91),  # Kolmoset > 9
    (13, 95),  # Suora
    (14, 97),  # Väri 
    (15, 98),  # Täyskäsi
    (16, 99),  # Neloset
    (17, 100)  # Värisuora
]


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