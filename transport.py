'''
class Transport:

    def __init__(self):
        self.transport = LocalTransport()

    def vaihdaNetworkiksi(self, ...):
        self.transport = NetworkTransport(...)
'''

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
        return viestit


    # Engine -> GUI

    def send_to_gui(self, viesti):
        self.to_gui.append(viesti)

    def receive_for_gui(self):
        viestit = self.to_gui
        self.to_gui = []
        return viestit



class NetworkTransport:

    pass