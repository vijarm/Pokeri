from Pakka import Kortti
from Pistelasku import laskeArvot, haeVoittaja
from Pelaaja import Pelaaja


def kortti(maa, numero):
    return Kortti(maa, numero)

def kasi(*kortit):
    return list(kortit)

#Yksikkötestit käsien luokitteluun


kasi1 = kasi(
    Kortti("RUUTU", 8), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 3), 
    Kortti("HERTTA", 4), 
    Kortti("HERTTA", 5))

kasi2 = kasi(
    Kortti("RUUTU", 12), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 3), 
    Kortti("HERTTA", 4), 
    Kortti("HERTTA", 5))

kasi3 = kasi(
    Kortti("RUUTU", 12), 
    Kortti("RUUTU", 2), 
    Kortti("PATA", 3), 
    Kortti("RISTI", 4), 
    Kortti("HERTTA", 5))

kasi4 = kasi3.copy()

print("Kädet ovat hai:ta:", laskeArvot(kasi1)["kasinimi"], "+", laskeArvot(kasi2)["kasinimi"], "+", laskeArvot(kasi3)["kasinimi"])
print("Kasi2 on suurempi kuin kasi1:", laskeArvot(kasi2)["vahvuus"] > laskeArvot(kasi1)["vahvuus"])
print("Kasi2 ja kasi3 tulee tasapeli:", laskeArvot(kasi2)["vahvuus"] == laskeArvot(kasi3)["vahvuus"])


kasi1 = kasi(
    Kortti("RUUTU", 8), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 3), 
    Kortti("HERTTA", 4), 
    Kortti("HERTTA", 8))

kasi2 = kasi(
    Kortti("RUUTU", 12), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 3), 
    Kortti("HERTTA", 4), 
    Kortti("HERTTA", 12))

kasi3 = kasi(
    Kortti("RUUTU", 12), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 3), 
    Kortti("HERTTA", 6), 
    Kortti("HERTTA", 12))

print("---------------------")
print("Kädet ovat pareja:", laskeArvot(kasi1)["kasinimi"], "+", laskeArvot(kasi2)["kasinimi"], "+", laskeArvot(kasi2)["kasinimi"])
print("kasi2 on suurempi kuin kasi1:", laskeArvot(kasi2)["vahvuus"] > laskeArvot(kasi1)["vahvuus"])
print("kasi3 on suurempi kuin kasi2 kicker-kortin avulla:", laskeArvot(kasi3)["vahvuus"] > laskeArvot(kasi2)["vahvuus"])
print("Pari voittaa hain:", laskeArvot(kasi1)["vahvuus"] > laskeArvot(kasi4)["vahvuus"])

kasi4 = kasi3.copy()


kasi1 = kasi(
    Kortti("RUUTU", 8), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 3), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 8))

kasi2 = kasi(
    Kortti("RUUTU", 12), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 3), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 12))

kasi3 = kasi(
    Kortti("RUUTU", 12), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 9), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 12))

print("---------------------")
print("Kädet ovat kahta paria:", laskeArvot(kasi1)["kasinimi"], "+", laskeArvot(kasi2)["kasinimi"], "+", laskeArvot(kasi3)["kasinimi"])
print("Kasi2 on suurempi kuin Kasi1:", laskeArvot(kasi2)["vahvuus"] > laskeArvot(kasi1)["vahvuus"])
print("Kasi3 on suurempi kuin Kasi2 kicker-kortin avulla:", laskeArvot(kasi3)["vahvuus"] > laskeArvot(kasi2)["vahvuus"])
print("Kaksi paria voittaa parin:", laskeArvot(kasi1)["vahvuus"] > laskeArvot(kasi4)["vahvuus"])

kasi4 = kasi3.copy()



kasi1 = kasi(
    Kortti("RUUTU", 8), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 8), 
    Kortti("HERTTA", 4), 
    Kortti("HERTTA", 8))

kasi2 = kasi(
    Kortti("RUUTU", 12), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 12), 
    Kortti("HERTTA", 4), 
    Kortti("HERTTA", 12))

kasi3 = kasi(
    Kortti("RUUTU", 12), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 12), 
    Kortti("HERTTA", 6), 
    Kortti("HERTTA", 12))

print("---------------------")
print("Kädet ovat kolmosia:", laskeArvot(kasi1)["kasinimi"], "+", laskeArvot(kasi2)["kasinimi"], "+", laskeArvot(kasi3)["kasinimi"])
print("Kasi2 on suurempi kuin Kasi1:", laskeArvot(kasi2)["vahvuus"] > laskeArvot(kasi1)["vahvuus"])
print("Kasi3 on suurempi kuin Kasi2 kicker-kortin avulla:", laskeArvot(kasi3)["vahvuus"] > laskeArvot(kasi2)["vahvuus"])
print("Kolmoset voittaa kaksi paria:", laskeArvot(kasi1)["vahvuus"] > laskeArvot(kasi4)["vahvuus"])

kasi4 = kasi3.copy()


kasi1 = kasi(
    Kortti("RUUTU", 4), 
    Kortti("HERTTA", 5), 
    Kortti("HERTTA", 6), 
    Kortti("HERTTA", 7), 
    Kortti("HERTTA", 8))

kasi2 = kasi(
    Kortti("RUUTU", 10), 
    Kortti("HERTTA", 11), 
    Kortti("HERTTA", 12), 
    Kortti("HERTTA", 13), 
    Kortti("HERTTA", 14))

kasi3 = kasi(
    Kortti("RUUTU", 14), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 3), 
    Kortti("HERTTA", 4), 
    Kortti("HERTTA", 5))

print("---------------------")
print("Kädet ovat suoria:", laskeArvot(kasi1)["kasinimi"], "+", laskeArvot(kasi2)["kasinimi"], "+", laskeArvot(kasi3)["kasinimi"])
print("Kasi2 10-A suora on suurempi kuin Kasi1 4-8 suora:", laskeArvot(kasi2)["vahvuus"] > laskeArvot(kasi1)["vahvuus"])
print("Kasi1 4-8 suora voittaa Kasi3 A-5 suoran:", laskeArvot(kasi1)["vahvuus"] > laskeArvot(kasi3)["vahvuus"])
print("Suora voittaa kolmoset:", laskeArvot(kasi3)["vahvuus"] > laskeArvot(kasi4)["vahvuus"])

kasi4 = kasi3.copy()



kasi1 = kasi(
    Kortti("HERTTA", 12), 
    Kortti("HERTTA", 11), 
    Kortti("HERTTA", 10), 
    Kortti("HERTTA", 8), 
    Kortti("HERTTA", 7))

kasi2 = kasi(
    Kortti("RUUTU", 13), 
    Kortti("RUUTU", 7), 
    Kortti("RUUTU", 6), 
    Kortti("RUUTU", 5), 
    Kortti("RUUTU", 3))

kasi3 = kasi(
    Kortti("RISTI", 13), 
    Kortti("RISTI", 7), 
    Kortti("RISTI", 6), 
    Kortti("RISTI", 5), 
    Kortti("RISTI", 4))


print("---------------------")
print("Kädet ovat värejä:", laskeArvot(kasi1)["kasinimi"], "+", laskeArvot(kasi2)["kasinimi"], "+", laskeArvot(kasi3)["kasinimi"])
print("Kasi2 voittaa kasi1 suuremmalla suurimmalla kortilla:", laskeArvot(kasi2)["vahvuus"] > laskeArvot(kasi1)["vahvuus"])
print("Kasi3 voittaa kasi2 suuremmalla pienimmällä kortilla:", laskeArvot(kasi3)["vahvuus"] > laskeArvot(kasi2)["vahvuus"])
print("Väri voittaa suoran:", laskeArvot(kasi1)["vahvuus"] > laskeArvot(kasi4)["vahvuus"])

kasi4 = kasi3.copy()



kasi1 = kasi(
    Kortti("RUUTU", 8), 
    Kortti("RISTI", 8), 
    Kortti("PATA", 8), 
    Kortti("HERTTA", 4), 
    Kortti("RUUTU", 4))

kasi2 = kasi(
    Kortti("RUUTU", 12), 
    Kortti("RISTI", 12), 
    Kortti("HERTTA", 12), 
    Kortti("RISTI", 4), 
    Kortti("PATA", 4))


print("---------------------")
print("Kädet ovat täyskäsiä:", laskeArvot(kasi1)["kasinimi"], "+", laskeArvot(kasi2)["kasinimi"])
print("Kasi2 voittaa kasi1 suuremmalla johtavalla kortilla:", laskeArvot(kasi2)["vahvuus"] > laskeArvot(kasi1)["vahvuus"])
print("Täyskäsi voittaa värin:", laskeArvot(kasi1)["vahvuus"] > laskeArvot(kasi4)["vahvuus"])

kasi4 = kasi2.copy()


kasi1 = kasi(
    Kortti("RUUTU", 8), 
    Kortti("RISTI", 8), 
    Kortti("PATA", 8), 
    Kortti("HERTTA", 8), 
    Kortti("RUUTU", 4))

kasi2 = kasi(
    Kortti("RUUTU", 12), 
    Kortti("RISTI", 12), 
    Kortti("HERTTA", 12), 
    Kortti("PATA", 12), 
    Kortti("PATA", 4))

print("---------------------")
print("Kädet ovat nelosia:", laskeArvot(kasi1)["kasinimi"], "+", laskeArvot(kasi2)["kasinimi"])
print("Kasi2 voittaa kasi1 suuremmalla johtavalla kortilla:", laskeArvot(kasi2)["vahvuus"] > laskeArvot(kasi1)["vahvuus"])
print("Neloset voittaa täyskäden:", laskeArvot(kasi1)["vahvuus"] > laskeArvot(kasi4)["vahvuus"])

kasi4 = kasi2.copy()



kasi1 = kasi(
    Kortti("HERTTA", 14), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 3), 
    Kortti("HERTTA", 5), 
    Kortti("HERTTA", 4))

kasi2 = kasi(
    Kortti("RUUTU", 8), 
    Kortti("RUUTU", 7), 
    Kortti("RUUTU", 6), 
    Kortti("RUUTU", 5), 
    Kortti("RUUTU", 4))

print("---------------------")
print("Kädet ovat värisuoria:", laskeArvot(kasi1)["kasinimi"], "+", laskeArvot(kasi2)["kasinimi"])
print("Kasi2 suora 4-8 voittaa kasi1 suoran A-5:", laskeArvot(kasi2)["vahvuus"] > laskeArvot(kasi1)["vahvuus"])
print("Värisuora voittaa neloset:", laskeArvot(kasi1)["vahvuus"] > laskeArvot(kasi4)["vahvuus"])


pelaaja1 = Pelaaja("pelaaja1", "testi")
pelaaja2 = Pelaaja("pelaaja2", "testi")
pelaaja3 = Pelaaja("pelaaja3", "testi")
pelaaja4 = Pelaaja("pelaaja4", "testi")

pelaaja1.kasikortit = kasi(
    Kortti("RUUTU", 12), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 12), 
    Kortti("HERTTA", 4), 
    Kortti("HERTTA", 12))

pelaaja2.kasikortit = kasi(
    Kortti("RUUTU", 4), 
    Kortti("HERTTA", 5), 
    Kortti("HERTTA", 6), 
    Kortti("HERTTA", 7), 
    Kortti("HERTTA", 8))

pelaaja3.kasikortit = kasi(
    Kortti("RUUTU", 12), 
    Kortti("HERTTA", 2), 
    Kortti("HERTTA", 3), 
    Kortti("HERTTA", 4), 
    Kortti("HERTTA", 12))

pelaaja4.kasikortit = kasi(
    Kortti("RUUTU", 12), 
    Kortti("RUUTU", 2), 
    Kortti("PATA", 3), 
    Kortti("RISTI", 4), 
    Kortti("HERTTA", 5))

voittaja = haeVoittaja([pelaaja1, pelaaja2, pelaaja3, pelaaja4])

print("---------------------")
print("haeVoittaja funktio löytää voittajaksi pelaaja2, jolla kädessä suora:")
print("Voittaja:", voittaja[0]["pelaaja"].nimi, "|| käsi:", voittaja[0]["kasinimi"])

voittaja = haeVoittaja([pelaaja1, pelaaja3, pelaaja4])
print("toiseksi tulee pelaaja1, jolla kädessä kolmoset:")
print("Voittaja:", voittaja[0]["pelaaja"].nimi, "|| käsi:", voittaja[0]["kasinimi"])


print("---------------------")
print("Testit suoritettu.")