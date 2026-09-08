from Pistelasku import laskeArvot
from Pelaaja import Pelaaja
from Pelipoyta import Pelipoyta
from GUI.GUI import GUI
from transport import Transport
from viestit import Paivitys, Komento


class Peli:
    '''Koko pelin pääluokka'''

    def __init__(self, gui=None):
        self.pelipoyta = None
        self.gui = gui
        self.running = True
        self.mode = "valikko"
        self.komennot = []  #GUI:sta enginelle tulleet
        self.menu_paivitykset = []  #Valikosta GUI:lle siirtyvät
        self.client_pelaaja = {}
        self.pelaaja_client = {}
        self.oma_pelaaja = Pelaaja("PokrChmp", "host")
        self.pelaajat = [self.oma_pelaaja, None, None, None]

        self.simulointi = None

        self.transport = Transport()

    def paivitaTila(self):
        '''Pelin tai simuloinnin ollessa käynnissä päivitetään jokaisella tickillä pelin tila'''

        if self.mode == "pelipoyta":

            if self.pelipoyta is not None:

                if self.pelipoyta.tila == "valmis":  #odotetaan GUI OK:ta normipelissä
                    return

                self.pelipoyta.paivitaTila()

        elif self.mode == "simulointi":

            if self.simulointi is not None:

                if self.simulointi.valmis == True:
                    #self.simulointi.tulosta()
                    self.paivitys_to_gui("simulointi_tulokset", {"tulokset": self.simulointi.get_tulokset()})
                    self.mode = "valikko"
                    return

                self.simulointi.pelaa()



    def kasitteleKomento(self, komento, client):
        '''Käsittelee GUI:lta enginelle tulevat komennot'''

        #print("Käsitellään komento", komento.tapahtuma, komento.tiedot)

        if komento.tapahtuma == "poistu_pelipoydasta":

            if client is None:
                if self.pelipoyta is not None:
                    for pelaaja in self.pelipoyta.pelaajat:
                        pelaaja.nollaaKokoPeli()
                    self.pelipoyta = None

            self.transport.vaihdaLocaliksi()

            for i, pelaaja in enumerate(self.pelaajat):
                if pelaaja is not None:
                    if pelaaja.tyyppi == "client":
                        self.pelaajat[i] = None
                        socket = self.pelaaja_client.pop(pelaaja)
                        self.client_pelaaja.pop(socket)

            self.paivitys_to_gui("uusipelaajalista", {"pelaajat": self.pelaajat})
            self.paivitys_to_gui("vaihda_gui_mode", {"uusi_mode": "valikko"})
            self.mode = "valikko"

            print(f"Pelaaja {komento.pelaaja} poistui pelistä.")
            return

        if komento.tapahtuma == "host_disconnect":
            self.transport.vaihdaLocaliksi()


        if self.mode == "valikko":

            #pelaajavalikko

            if komento.tapahtuma == "muokkaa_pelaajaa":
                komento.pelaaja.muokkaa(komento.tiedot)
                return

            elif komento.tapahtuma == "luo_pelaaja":
                pelaaja = self.luoPelaaja(komento.tiedot)
                self.pelaajat[komento.tiedot["indeksi"]] = pelaaja
                self.paivitys_to_gui("uusipelaajalista", {"pelaajat": self.pelaajat})
                return

            elif komento.tapahtuma == "luo_simulointi_pelaaja":
                pelaaja = self.luoPelaaja(komento.tiedot)
                self.paivitys_to_gui("uusi_simulointi_pelaaja", {"pelaaja": pelaaja, "indeksi": komento.tiedot["indeksi"]})
                return

            elif komento.tapahtuma == "poista_pelaaja":
                pelaaja = komento.pelaaja
                if pelaaja.tyyppi == "client":
                    self.paivitys_to_player(pelaaja, "host_perui", {})
                    socket = self.pelaaja_client.pop(pelaaja)
                    self.client_pelaaja.pop(socket)

                self.pelaajat[komento.tiedot["indeksi"]] = None
                self.paivitys_to_gui("uusipelaajalista", {"pelaajat": self.pelaajat})


            elif komento.tapahtuma == "sulje_peli":
                self.running = False
                return

            elif komento.tapahtuma == "aloita_peli":
                self.transport.esta_liittyminen()

                self.varmistaKaikkienNimet()

                self.pelipoyta = Pelipoyta([p for p in self.pelaajat if p is not None], self.paivitys_to_player) 
                self.pelipoyta.paivitaNakymat()

                for p in self.pelipoyta.pelaajat:
                    if p.ai is None:
                        self.paivitys_to_player(p, "aloita_peli", {"uusi_mode": "pelipoyta"}, p.nakyma)

                self.mode = "pelipoyta"
                return

            #pelaajavalikon hostin komennot

            elif komento.tapahtuma == "salli_liittyminen":
                onnistui, virhe = self.transport.salli_liittyminen()
                if onnistui:
                    self.paivitys_to_gui("liittyminen_sallittu", {})
                else:
                    self.paivitys_to_gui("host_epaonnistui", {"virhe": virhe})

            elif komento.tapahtuma == "esta_liittyminen":
                self.transport.esta_liittyminen()
                self.paivitys_to_gui("liittyminen_estetty", {})

            elif komento.tapahtuma == "sulje_host":
                self.nollaaVerkkopeli()


            elif komento.tapahtuma == "poista_client":
                pelaaja = komento.pelaaja
                socket = self.pelaaja_client.pop(pelaaja)
                self.client_pelaaja.pop(socket)


            #online peliin liittyminen (itse client)

            elif komento.tapahtuma == "liity_online":
                nimi = komento.tiedot["nimi"]
                ip = komento.tiedot["ip"]
                onnistui, virhe = self.transport.vaihdaNetworkiksi(mode="client", host=ip, port=5000)      

                if onnistui:
                    self.transport.send_to_engine(Komento("liity_pelaajaksi", nimi))
                    #Onnistumisen kuittaus lähetetään kun tulee Paivityksena takaisin hostilta

                else:
                    self.paivitys_to_gui("client_epaonnistui", {"virhe": virhe})
                return

            elif komento.tapahtuma == "peru_online":
                self.transport.vaihdaLocaliksi()
                self.mode = "valikko"
                self.paivitys_to_gui("vaihda_gui_mode", {"uusi_mode": "valikko"})
                return


            #clientiltä hostille tulevat viestit ennen pelin aloittamista

            elif komento.tapahtuma == "liity_pelaajaksi":
                assert len(self.client_pelaaja) <= 4, "Ihmispelaajia on max 4, transport ei päästä yli 3 clientiä läpi (alkuun vain 1)"
                nimi = komento.pelaaja  #Tässä kohtaa tulee vain nimi, engine luo olion
                nimi = self.varmistaVapaaNimi(nimi)
                pelaaja = Pelaaja(nimi, "client")

                vapaa_paikka = None
                for i, p in enumerate(self.pelaajat):
                    if p == None:
                        vapaa_paikka = i
                        break
                    elif p.ai is not None:
                        vapaa_paikka = i

                if vapaa_paikka == None:
                    assert(vapaa_paikka is not None), "Ei pitäisi tulla tilannetta jossa ei ole tilaa, transport suodattaa"
                    return
                
                self.pelaajat[vapaa_paikka] = pelaaja
                self.client_pelaaja[client] = pelaaja
                self.pelaaja_client[pelaaja] = client
                
                self.paivitys_to_gui("uusi_client", {"pelaajat": self.pelaajat, "nimi": pelaaja.nimi})
                self.paivitys_to_player(pelaaja, "liittyminen_ok", {"nimi": pelaaja.nimi})
                return

            elif komento.tapahtuma == "client_disconnect":
                pelaaja = self.client_pelaaja.pop(client, None)

                if pelaaja is not None:
                    self.pelaaja_client.pop(pelaaja)
                    for i, p in enumerate(self.pelaajat):
                        if p == pelaaja:
                            self.pelaajat[i] = None  
                            break

                    self.paivitys_to_gui("client_poistui", {"pelaaja": pelaaja.nimi, "pelaajalista": self.pelaajat})
                return

            #Simulointi

            elif komento.tapahtuma == "aloita_simulointi":
                pelaajat = [p for p in komento.pelaaja if p is not None]
                pelien_maara = komento.tiedot["pelien_maara"]
                self.simulointi = Simulointi(pelaajat, pelien_maara, self.paivitys_to_gui)
                self.mode = "simulointi"
                return


        if self.mode == "simulointi":

            if komento.tapahtuma == "peru_simulointi":
                assert self.simulointi is not None, "Simulointi ei voi alkaa ilman simulointi-oliota"
                self.mode = "valikko"
                self.simulointi.valmis = True
                self.paivitys_to_gui("simulointi_tulokset", {"tulokset": self.simulointi.get_tulokset()})
                self.simulointi.tulosta()                
                return



        if self.mode == "pelipoyta":
            
            assert self.pelipoyta is not None

            if komento.tapahtuma == "vaihdot":
                
                if self.pelipoyta.jako is not None and self.pelipoyta.jako.vaihtoPelaaja is not None:

                    if komento.pelaaja != self.pelipoyta.jako.vaihtoPelaaja.nimi:
                        print("Väärä pelaaja yritti vaihtaa kortteja")
                        return

                    self.pelipoyta.jako.vaihtoindeksit = komento.tiedot["vaihtoindeksit"]

            elif komento.tapahtuma == "ok":
                self.pelipoyta.ok = True
                print(f"Pelaaja {komento.pelaaja} painoi OK.")

            elif komento.tapahtuma == "panostusvalinta":

                if self.pelipoyta.jako is not None and self.pelipoyta.jako.panostuskierros is not None and self.pelipoyta.jako.panostuskierros.pelaajaVuorossa is not None:
                
                    if komento.pelaaja != self.pelipoyta.jako.panostuskierros.pelaajaVuorossa.nimi:
                        print("Väärä pelaaja yritti antaa panostusvalintaa")
                        return
                    
                    self.pelipoyta.jako.panostuskierros.panostusValinta = komento.tiedot["panostusvalinta"]

            elif komento.tapahtuma == "peli_ohi":
                self.mode = "valikko"
                self.paivitys_to_gui("vaihda_gui_mode", {"uusi_mode": "valikko"})

                self.nollaaVerkkopeli()
                self.pelipoyta = None

            elif komento.tapahtuma == "client_disconnect":
                pelaaja = self.client_pelaaja.pop(client, None)

                if pelaaja is None:
                    return

                self.pelaaja_client.pop(pelaaja)

                pelaaja.valinta = 4
                pelaaja.folded = True
                pelaaja.aktiivinen = False
                pelaaja.tyyppi = "Tietsikka"

                if self.pelipoyta.jako is not None:
                    if pelaaja in self.pelipoyta.jako.mukanaPotissa:
                        self.pelipoyta.jako.mukanaPotissa.remove(pelaaja)

                #jos juuri kyseiseltä pelaajalta odotetaan vaihtoja tai panostusta
                if self.pelipoyta.jako is not None and self.pelipoyta.jako.vaihtoPelaaja == pelaaja:
                    self.pelipoyta.jako.vaihtoindeksit = []

                if self.pelipoyta.jako is not None and self.pelipoyta.jako.panostuskierros and self.pelipoyta.jako.panostuskierros.pelaajaVuorossa == pelaaja:
                    self.pelipoyta.jako.panostuskierros.panostusValinta = "luovuta"

                for i, p in enumerate(self.pelaajat):
                    if p == pelaaja:
                        self.pelaajat[i] = None
                        break


    def luoPelaaja(self, tiedot):
        '''Luo uuden pelaajan GUI:lta / verkosta tulleiden tietojen mukaisesti'''

        #AI-pelaajan luominen
        if tiedot["ai"] is not None:
            if tiedot["ai"] in ("Koneoppinut", "Koneoppinut 500k", "Koneoppinut 1M", "Koneoppinut 2M", "Koneoppinut 5M"): 
                luokka = "Koneoppinut" # Nämä kuuluisi oikeasti yhdeksi pääluokaksi ja malli pitäisi olla oma erillinen valinta GUI:ssa...
                malli = tiedot["ai"]
            else:
                luokka = tiedot["ai"]
                malli = None
            asetukset = {"aggressiivisuus": tiedot["ai_aggressiivisuus"], "luokka": luokka, "strategia": tiedot["ai_strategia"], "malli": malli}
            return Pelaaja(tiedot["nimi"], tiedot["tyyppi"], luokka, asetukset)

        #Ihmispelaajan luominen
        else:
            return Pelaaja(tiedot["nimi"], tiedot["tyyppi"])

    def varmistaVapaaNimi(self, nimi, ohita=None):  
        '''Pelaajilla ei ole erillistä ID:tä vaan nimi on tunniste. Funktio lisää nimen perään numeroita, mikäli nimi on jo käytössä.'''

        alkuperainen = nimi
        numero = 1

        while True:
            nimi_varattu = any(p is not None and p is not ohita and p.nimi == nimi for p in self.pelaajat)

            if not nimi_varattu:
                return nimi

            nimi = f"{alkuperainen}{numero}"
            numero += 1

    def varmistaKaikkienNimet(self):
        '''Varmistaa, että kaikilla pelin aloittavilla pelaajilla on uniikit nimet.'''
        for pelaaja in self.pelaajat:
            if pelaaja is None:
                continue

            pelaaja.nimi = self.varmistaVapaaNimi(pelaaja.nimi, ohita=pelaaja)

    def nollaaVerkkopeli(self):
        '''Nollaa kaikki verkkopelin tiedot, tyhjentää client-pelaaja-client listat, sekä yleisen pelaajalistan muista paitsi omasta pelaajasta.'''
        self.transport.vaihdaLocaliksi()
        self.client_pelaaja.clear()
        self.pelaaja_client.clear()
        self.pelaajat = [self.oma_pelaaja, None, None, None]
        self.oma_pelaaja.nollaaKokoPeli()
        self.paivitys_to_gui("uusipelaajalista", {"pelaajat": self.pelaajat})



    def paivitys_to_gui(self, tyyppi, tiedot, nakyma=None):
        '''Lähettää engineltä päivityksen omalle GUI:lle'''

        paivitys = Paivitys(tyyppi, tiedot, nakyma)
        self.transport.send_to_own_gui(paivitys)

    def paivitys_to_player(self, pelaaja, tyyppi, tiedot, nakyma=None):
        '''Lähettää engineltä päivityksen tietyn pelaajan GUI:lle'''

        paivitys = Paivitys(tyyppi, tiedot, nakyma)

        if pelaaja.tyyppi == "host":
            self.transport.send_to_own_gui(paivitys)

        elif pelaaja.tyyppi == "client":
            client = self.pelaaja_client[pelaaja]
            self.transport.send_to_client(client, paivitys)

    def paivitys_to_all_gui(self, tyyppi, tiedot, nakyma=None):
        '''Lähettää engineltä päivityksen kaikkien pelaajien GUI:lle'''

        paivitys = Paivitys(tyyppi, tiedot, nakyma)
        self.transport.send_to_all_gui(paivitys)



class Simulointi:
    '''Simulointi-olio, johon kerätään tilastot simuloinnin aikana tapahtuvien pelien tuloksista ja esiintyneistä käsiluokista.'''

    def __init__(self, pelaajat, peleja, paivitys_to_gui):
        self.pelaajat = pelaajat
        self.peleja = peleja
        self.paivitys_to_gui = paivitys_to_gui
        self.pelattu = 0
        self.valmis = False

        self.pelatutKadet = 0
        self.tasapelit = 0
        self.voitot = {}  #Koko pelit

        self.kasivoitot = {}  #Yksittäiset kädet
        self.fold_voitot = {}  #Fold-voitot
        self.voittokadet = {}  #Käsi jolla voitettiin
        self.parasHaviaja = {}  #Paras käsi joka hävisi

        for pelaaja in self.pelaajat:
            self.voitot[pelaaja] = 0
            self.kasivoitot[pelaaja] = 0
            self.fold_voitot[pelaaja] = 0

        for i in range(18):
            self.voittokadet[i] = 0
            self.parasHaviaja[i] = 0

    def pelaa(self):
        '''Pelaa -funktio ajetaan simuloinnissa jokaisella tickillä. Yhden tickin aikana peli simuloi 10 kokonaista peliä alusta loppuun.'''

        for _ in range(10): 
            simulointi_peli = Pelipoyta(self.pelaajat, simulointi = self)
            while True:
                simulointi_peli.paivitaTila()
                if simulointi_peli.tila == "valmis":
                    break
        
            self.voitot[simulointi_peli.voittaja] += 1

            for p in self.pelaajat:
                p.nollaaKokoPeli()

            self.pelattu += 1
            if self.pelattu >= self.peleja:
                self.valmis = True
                break

        #Lähetetään GUI:lle päivityksenä pelattujen pelien osuus simulointiin valitusta kokonaispelimäärästä.
        self.paivitys_to_gui("simulointi_paivitys", {"pelattu": int((self.pelattu / self.peleja) * 100)})
                        
    def tulosta(self):
        '''Tulosta -apufunktio, debug/testi-käytössä, jos simuloinnin tietoja haluaa tekstinä terminaliin.'''

        print("SIMULOINTI VALMIS, KÄSIÄ PELATTIIN YHTEENSÄ", self.pelatutKadet, "KPL", self.pelattu, "PELISSÄ")
        for pelaaja, voitot in self.voitot.items():
            print("PELAAJA:", pelaaja.nimi, "|| VOITOT:", voitot, "|| FOLD-VOITOT:", self.fold_voitot[pelaaja], "|| KÄSIVOITOT:", self.kasivoitot[pelaaja], "|| LISÄTIEDOT:", pelaaja.ai_tyyppi, pelaaja.ai.asetukset)
        print("============================  VOITTOKÄDET  =========================")
        for kasi, arvo in self.voittokadet.items():
            print("KÄSI:", kasi, "|| VOITTOJA:", arvo)
        print("==========================  PARHAAT HÄVIÄJÄT  =========================")
        for kasi, arvo in self.parasHaviaja.items():
            print("KÄSI:", kasi, "|| VOITTOJA:", arvo)

    def get_tulokset(self):
        '''Palauttaa simulointi-olioon kerätyt tilastot'''

        tulokset = {
            "pelit": self.pelattu,
            "pelatut_kadet": self.pelatutKadet,
            "voitot": self.voitot,
            "tasapelit": self.tasapelit,
            "kasivoitot": self.kasivoitot,
            "fold_voitot": self.fold_voitot,
            "voittokadet": self.voittokadet,
            "parasHaviaja": self.parasHaviaja
        }

        return tulokset


def main():
    '''Main -funktio, käynnistää pelin.'''

    peli = Peli()
    gui = GUI(peli.oma_pelaaja, peli.transport)
    peli.gui = gui
    peli.oma_pelaaja.gui = gui
    dt = 0

    while peli.running:

        peli.gui.process_events()

        for client, komento in peli.transport.receive_for_engine():
            peli.kasitteleKomento(komento, client)

        peli.paivitaTila()
        peli.gui.paivita(dt)  #fps
        peli.gui.draw()

        dt = peli.gui.clock.tick(60) / 1000


if __name__ == "__main__":
    main()