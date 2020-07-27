class Loup:
    """Class qui défini une partie de Loup-Garou"""
    def __init__(self):
        self.maxPlayer = 15
        self.status = "Out"
        self.nbPlayer = 0
        self.Players = []
    def reset(self):
        return Loup.__init__(self)
    
    def checkUsernames(self, username):
        for player in self.Players:
            if player["username"] == username:
                return False
        return True
    
    def addPlayer(self, username):
        """Ajoute un joueur si il n'est pas encore dedans. Renvois False en cas d'erreur"""
        if self.Players != [] and self.checkUsernames(username) is False:
            return False
        self.Players.append({"username":username, "role":"undefined"})
        self.nbPlayer = len(self.Players)
    def removePlayer(self, username):
        """Retire un joueur si il est dans la liste des joueurs. Renvois False en cas d'erreur"""
        if self.Players == []:
            return False
        self.Players = [player for player in self.Players if player["username"] != username]
        if self.nbPlayer == len(self.Players):
            return False
        else:
            self.nbPlayer = len(self.Players)
            return True