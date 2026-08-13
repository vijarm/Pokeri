
class AI:
    def __init__(self):
        self.tyyppi = "Default"

    def vaihdaKortit(self):
        NotImplemented

    def teePanostus(self):
        NotImplemented


class randomAI(AI):
    def vaihdaKortit(self):
        #Tähän joku rand in len montako vaihtoehtoa suosituksissa... Jotenkin näin se rakenne alkaa
        return super().vaihdaKortit()

    def teePanostus(self):
        #Tähän jotain että 0,4 call 0,4 raise 0,2 fold ...
        