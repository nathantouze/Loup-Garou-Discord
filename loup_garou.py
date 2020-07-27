import config

class LoupGarou:
    """Class qui défini une partie de Loup-Garou"""
    def __init__(self):
        self.maxPlayer = config.maxPlayer
        self.status = "Out"
        self.nbPlayer = 0
        self.Players = []
        self.gameChief = None

    def reset(self):
        return LoupGarou.__init__(self)
    

    def startGame(self):
        self.status = "Playing"

    def checkUsernames(self, username):
        if username.bot == True:
            return False
        for player in self.Players:
            if player["username"] == str(username):
                return False
        return True
    
    def addPlayer(self, username, id):
        """Ajoute un joueur si il n'est pas encore dedans. Renvois False en cas d'erreur"""
        if self.Players != [] and self.checkUsernames(username) is False or username.bot is True:
            return False
        self.Players.append({"username":str(username), "id":id, "role":"undefined"})
        self.nbPlayer = len(self.Players)
    def removePlayer(self, id):
        """Retire un joueur si il est dans la liste des joueurs. Renvois False en cas d'erreur"""
        if self.Players == []:
            return False
        self.Players = [player for player in self.Players if player["id"] != id]
        if self.nbPlayer == len(self.Players):
            return False
        else:
            self.nbPlayer = len(self.Players)
            return True