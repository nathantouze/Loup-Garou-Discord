from threading import Thread



class GameLoop(Thread):
    """Classe définissant la boucle de jeu du Loup-Garou."""
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        print("je sais pas comment gérer ça :'(")