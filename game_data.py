import config
import random
import roles


class LPData:
    """Class qui défini une partie de Loup-Garou"""
    def __init__(self):
        self.status = "Out"
        self.nbPlayer = 0
        self.players = []
        self.gameChief = None
        self.invite = None

    def reset(self):
        return LPData.__init__(self)
    

    def checkGameInit(self, plan):
        if plan != []:
            return False
        for player in self.players:
            if player["role"] is None:
                return False
        return True

    def roleDistribution(self):
        """Distribue les rôles. Envois un message à tout les joueurs avec les explications correspondantes."""
        construct_plan = list(config.roles_per_players[self.nbPlayer])
        index = 0
        while self.checkGameInit(construct_plan) is False and index < self.nbPlayer:
            role = random.choice(construct_plan)
            if role == "loup-garou":
                self.players[index]["role"] = roles.Loup()
            elif role == "villageois":
                self.players[index]["role"] = roles.Villageois()
            elif role == "voyante":
                self.players[index]["role"] = roles.Voyante()
            elif role == "sorcière":
                self.players[index]["role"] = roles.Sorciere()
            elif role == "cupidon":
                self.players[index]["role"] = roles.Cupidon()
            elif role == "chasseur":
                self.players[index]["role"] = roles.Chasseur()
            else:
                return False
            construct_plan.remove(role)
            index += 1

    def startGame(self, game_channel):
        """Initialise la partie."""
        self.status = "Playing"
        self.roleDistribution()

    def isOver(self):
        """Renvois True si la partie est fini, False si elle ne l'est pas."""
        isWolf = False
        isVillager = False
        isLover = False
        for player in self.players:
            if player["role"].name == "loup-garou" and player["role"].alive is True:
                isWolf = True
            elif player["role"].name != "loup-garou" and player["role"].alive is True:
                isVillager = True
            elif player["role"].team == 3 and player["role"].alive is True:
                isLover = True
        if isWolf is True and isVillager is True and isLover is True and len(self.players) == 2: #check for lovers in different team end
            return True
        elif (isWolf is True and isVillager is False) or (isWolf is False and isVillager is True): #check for basic end
            return True
        elif isWolf is False and isLover is False and isVillager is False: #check for error
            return True
        else:
            return False

    def checkUsernames(self, user):
        for player in self.players:
            if str(player["user"]) == str(user):
                return False
        return True
    

    def addPlayer(self, user, id):
        """Ajoute un joueur si il n'est pas encore dedans. Renvois False en cas d'erreur"""
        if self.players != [] and self.checkUsernames(user) is False:
            return False
        #if user.bot is True:
        #    return False
        self.players.append({"user":user, "id":id, "role":None})
        self.nbPlayer = len(self.players)
        return True


    def removePlayer(self, id):
        """Retire un joueur si il est dans la liste des joueurs. Renvois False en cas d'erreur"""
        if self.players == []:
            return False
        self.players = [player for player in self.players if player["id"] != id]
        if self.nbPlayer == len(self.players):
            return False
        else:
            self.nbPlayer = len(self.players)
            return True

    def getPlayerByName(self, name=str):
        """Recherche un joueur en fontion de son nom. Le nom doit être une string. Renvoit None si le nom n'est pas présent."""
        for player in self.players:
            if str(player["user"]) == name:
                return player
        return None

    def getPlayerByID(self, id=int):
        """Recherche un joueur en fonction de son id. L'id doit être un int. Renvois None si l'id n'est pas présent."""
        for player in self.players:
            if player["id"] == id:
                return player
        return None

    def getFirstPlayerByRole(self, role=str):
        """Recherche un joueur en fonction de son role. Le rôle doit être une string (ref. Roles.py). Renvois None si le rôle n'est pas présent."""
        for player in self.players:
            if player["role"].name == role:
                return player
        return None

    def getPlayersByRole(self, role=str):
        """Recherche tout les joueurs avec un role défini. Le rôle doit être une string (ref. Roles.py). Renvois une liste vide si le rôle n'est pas présent."""
        role_list = list()
        for player in self.players:
            if player["role"].name == role:
                role_list.append(player)
        return role_list
