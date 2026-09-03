
import json
import socket

from viestit import Komento, Paivitys

class Transport:

    def __init__(self):
        self.transport = LocalTransport()

    def vaihdaNetworkiksi(self, mode, host=None, port=5000):
        self.transport.close()
        try:
            self.transport = NetworkTransport(mode, host, port)
            return True, None

        except OSError as e:
            self.transport = LocalTransport()
            return False, str(e)

    def vaihdaLocaliksi(self):
        self.transport.close()
        self.transport = LocalTransport()

    def send_to_engine(self, viesti):
        self.transport.send_to_engine(viesti)

    def receive_for_engine(self):
        return self.transport.receive_for_engine()

    def send_to_all_gui(self, viesti):
        self.transport.send_to_all_gui(viesti)
    
    def send_to_own_gui(self, viesti):
        self.transport.send_to_own_gui(viesti)

    def send_to_own_engine(self, viesti):
        self.transport.send_to_own_engine(viesti)

    def send_to_client(self, client, viesti):
        self.transport.send_to_client(client, viesti)

    def receive_for_gui(self):
        return self.transport.receive_for_gui()

    def close(self):
        self.transport.close()

    def salli_liittyminen(self):
        if isinstance(self.transport, NetworkTransport):
            self.transport.salliLiittyminen = True
            return True, None

        onnistui, virhe = self.vaihdaNetworkiksi(mode="host", host="", port=5000)
        if onnistui:
            assert isinstance(self.transport, NetworkTransport)
            self.transport.salliLiittyminen = True
            return True, None

        return False, virhe

    def esta_liittyminen(self):
        if isinstance(self.transport, NetworkTransport):
            self.transport.salliLiittyminen = False


#Local siirtää vain oliot sellaisenaan engine <-> gui, ei tarvita muutoksia väliin
class LocalTransport:

    def __init__(self):
        self.to_engine = []
        self.to_gui = []


    # GUI -> Engine

    def send_to_engine(self, viesti):
        self.to_engine.append(viesti)

    def receive_for_engine(self):
        viestit = self.to_engine
        self.to_engine = []
        return [(None, viesti) for viesti in viestit]

    # Engine -> GUI

    def send_to_own_gui(self, viesti):
        self.to_gui.append(viesti)

    def send_to_all_gui(self, viesti):
        self.to_gui.append(viesti)

    def send_to_client(self, client, viesti):
        # Local-pelissä ei ole client-yhteyksiä.
        pass

    def send_to_own_engine(self, viesti):
        self.to_engine.append(viesti)

    def receive_for_gui(self):
        viestit = self.to_gui
        self.to_gui = []
        return viestit


    def close(self):
        self.to_engine.clear()
        self.to_gui.clear()


#Nettipeliin tarvittava transportteri
class NetworkTransport:

    def __init__(self, mode, host=None, port=5000):
        self.mode = mode
        self.host = host
        self.port = port

        self.to_engine = []
        self.to_gui = []

        self.socket = None

        # Hostilla lista Client-yhteyksistä
        self.clients = []
        self.salliLiittyminen = True

        # Jokaiselle socketille oma vastaanottopuskuri
        self.buffers = {}

        if self.mode == "host":
            self._aloita_host()

        elif self.mode == "client":
            self._aloita_client()

        else:
            raise ValueError("mode pitää olla 'host' tai 'client'")

    # --------------------------------------------------
    # HOST
    # --------------------------------------------------

    def _aloita_host(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind((self.host, self.port))
        self.socket.listen()

        # Ei jäädä odottamaan connectia tähän kohtaan
        self.socket.setblocking(False)

        print(f"Host kuuntelee portissa {self.port}")

    def _hyvaksy_uudet_clientit(self):
        while True:
            try:
                client_socket, address = self.socket.accept()

            except BlockingIOError:
                break

            if not self.salliLiittyminen:
                print("Liittymisyritys hylätty:", address)
                client_socket.close()
                continue

            if len(self.clients) >= 1: #Alkuun nyt vaan 1 pelaaja
                print("Peli täynnä, liittymisyritys hylätty:", address)
                client_socket.close()
                continue

            client_socket.setblocking(False)

            self.clients.append(client_socket)
            self.buffers[client_socket] = b""

            print("Uusi client liittyi:", address)

    # --------------------------------------------------
    # CLIENT
    # --------------------------------------------------

    def _aloita_client(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)

        self.socket.connect((self.host, self.port))
        self.socket.setblocking(False)

        self.buffers[self.socket] = b""

        print(f"Yhdistetty hostiin {self.host}:{self.port}")

    # --------------------------------------------------
    # SERIALISOINTI
    # --------------------------------------------------

    def _serialisoi(self, obj):

        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj

        if isinstance(obj, list):
            return [self._serialisoi(x) for x in obj]

        if isinstance(obj, dict):
            return {
                key: self._serialisoi(value)
                for key, value in obj.items()
            }

        if hasattr(obj, "to_dict"):
            return {
                "__type__": obj.__class__.__name__,
                "data": self._serialisoi(obj.to_dict())
            }

        raise TypeError(f"Objektia {type(obj).__name__} ei voida serialisoida")

    # --------------------------------------------------
    # DESERIALISOINTI
    # --------------------------------------------------

    def _deserialisoi(self, data):

        if isinstance(data, list):
            return [self._deserialisoi(x) for x in data]

        if isinstance(data, dict):

            if "__type__" in data:

                tyyppi = data["__type__"]
                sisalto = data["data"]

                if tyyppi == "Kortti":
                    from Pakka import Kortti
                    return Kortti.from_dict(self._deserialisoi(sisalto))

                if tyyppi == "Komento":
                    return Komento.from_dict(self._deserialisoi(sisalto))

                if tyyppi == "Paivitys":
                    return Paivitys.from_dict(self._deserialisoi(sisalto))

                if tyyppi == "PelaajaNakyma":
                    from Pelaaja import PelaajaNakyma
                    return PelaajaNakyma.from_dict(self._deserialisoi(sisalto))

                if tyyppi == "MuutNakee":
                    from Pelaaja import MuutNakee
                    return MuutNakee.from_dict(self._deserialisoi(sisalto))

                raise TypeError(f"Tuntematon verkkotyyppi: {tyyppi}")

            return {
                key: self._deserialisoi(value)
                for key, value in data.items()
            }

        return data

    # --------------------------------------------------
    # LÄHETYS
    # --------------------------------------------------

    def _laheta(self, socket, viesti):

        data = self._serialisoi(viesti)
        teksti = json.dumps(data, ensure_ascii=False) + "\n"

        socket.sendall(teksti.encode("utf-8"))

    # --------------------------------------------------
    # VASTAANOTTO
    # --------------------------------------------------

    def _vastaanota_socketilta(self, socket):

        try:
            data = socket.recv(4096)

        except BlockingIOError:
            return []

        except (ConnectionAbortedError, ConnectionResetError, OSError):
            return None

        if not data:
            return None

        self.buffers[socket] += data

        viestit = []

        while b"\n" in self.buffers[socket]:

            data, self.buffers[socket] = \
                self.buffers[socket].split(b"\n", 1)

            if data:
                teksti = data.decode("utf-8")
                data = json.loads(teksti)
                viesti = self._deserialisoi(data)
                viestit.append(viesti)

        return viestit

    # --------------------------------------------------
    # ENGINE
    # --------------------------------------------------

    def receive_for_engine(self):

        if self.mode == "host":
            self._hyvaksy_uudet_clientit()

            for client in self.clients.copy():

                try:
                    viestit = self._vastaanota_socketilta(client)

                except (ConnectionResetError, OSError):
                    viestit = None

                if viestit is None:
                    print("Client tippui")
                    self.clients.remove(client)
                    self.buffers.pop(client, None)
                    client.close()

                    self.to_engine.append((client, Komento("client_disconnect", None)))

                    continue

                for viesti in viestit:
                    self.to_engine.append((client, viesti))

        '''elif self.mode == "client":  #Client ei (toistaiseksi ainakaan) vastaanota mitään engine-viestejä vaan vain gui:ta

            viestit = self._vastaanota_socketilta(self.socket)

            if viestit:
                for viesti in viestit:
                    self.to_engine.append((None, viesti))'''

        viestit = self.to_engine
        self.to_engine = []

        return viestit

    # --------------------------------------------------
    # GUI
    # --------------------------------------------------

    def send_to_engine(self, viesti):
        if self.mode == "host":
            # GUI -> Hostin engine on paikallinen
            self.to_engine.append((None, viesti))

        else:
            # Client GUI -> verkkoon Hostille
            self._laheta(self.socket, viesti)

    #Kaikille pelaajille
    def send_to_all_gui(self, viesti):
        if self.mode == "host":

            # Hostin oma GUI
            self.to_gui.append(viesti)

            # Kaikille Clienteille
            for client in self.clients.copy():
                try:
                    self._laheta(client, viesti)
                except (BrokenPipeError, ConnectionResetError, OSError):
                    print("Client tippui")
                    self.clients.remove(client)
                    self.buffers.pop(client, None)
                    client.close()

        else:
            # Clientin engine -> Clientin oma GUI
            self.to_gui.append(viesti)

    #Yhdelle tietylle clientille
    def send_to_client(self, client, viesti):
        try:
            self._laheta(client, viesti)
        except (BrokenPipeError, ConnectionResetError, OSError):
            print("Client tippui")
            if client in self.clients:
                self.clients.remove(client)
            self.buffers.pop(client, None)
            client.close()

    #Vain omalle gui:lle
    def send_to_own_gui(self, viesti):
        self.to_gui.append(viesti)

    def send_to_own_engine(self, viesti):
        self.to_engine.append((None, viesti))

    def receive_for_gui(self):

        if self.mode == "client":

            viestit = self._vastaanota_socketilta(self.socket)

            if viestit is None:
                print("HOST DISCONNECT HAVAITTU")
                self.to_gui.append(Paivitys("host_disconnect", {}))

            if viestit:
                self.to_gui.extend(viestit)

        viestit = self.to_gui
        self.to_gui = []

        return viestit

    def close(self):
        # Host sulkee kaikki client-yhteydet
        for client in self.clients:
            client.close()

        self.clients.clear()
        self.buffers.clear()

        # Suljetaan client socket
        if self.socket is not None:
            self.socket.close()
            self.socket = None
