import config
import random
import roles

class LoupGarou:
    """Class qui défini une partie de Loup-Garou"""
    def __init__(self, bot):
        self.maxPlayer = config.max_player
        self.status = "Out"
        self.nbPlayer = 0
        self.Players = []
        self.gameChief = None
        self.client = bot

    def reset(self):
        return LoupGarou.__init__(self, self.client)
    

    def checkGameInit(self, plan):
        if plan != []:
            return False
        for player in self.Players:
            if player["role"] is None:
                return False
        return True

    async def roleDistribution(self):
        """Distribue les rôles. Envois un message à tout les joueurs avec les explications correspondantes."""
        construct_plan = list(config.roles_per_players[self.nbPlayer])
        index = 0
        while self.checkGameInit(construct_plan) is False and index < self.nbPlayer:
            role = random.choice(construct_plan)
            if role == "loup-garou":
                self.Players[index]["role"] = roles.Loup()
            elif role == "villageois":
                self.Players[index]["role"] = roles.Villageois()
            elif role == "voyante":
                self.Players[index]["role"] = roles.Voyante()
            elif role == "sorcière":
                self.Players[index]["role"] = roles.Sorciere()
            elif role == "cupidon":
                self.Players[index]["role"] = roles.Cupidon()
            elif role == "chasseur":
                self.Players[index]["role"] = roles.Chasseur()
            else:
                return False
            await self.client.get_user(self.Players[index]["id"]).send("Tu es " + self.Players[index]["role"].name + "\n\n" + self.Players[index]["role"].description)
            construct_plan.remove(role)
            index += 1

    async def startGame(self):
        """Initialise la partie."""
        self.status = "Playing"
        await self.roleDistribution()
        await self.client.get_channel(config.game_channel_id).send("La partie commence !")


    def checkUsernames(self, user):
        for player in self.Players:
            if str(player["user"]) == str(user):
                return False
        return True
    

    def addPlayer(self, user, id):
        """Ajoute un joueur si il n'est pas encore dedans. Renvois False en cas d'erreur"""
        if self.Players != [] and self.checkUsernames(user) is False:
            return False
        if user.bot is True:
            return False
        self.Players.append({"user":user, "id":id, "role":None})
        self.nbPlayer = len(self.Players)
        return True


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

    def getPlayerByName(self, name=str):
        """Recherche un joueur en fontion de son nom. Le nom doit être une string. Renvoit None si le nom n'est pas présent."""
        for player in self.Players:
            if str(player["user"]) == name:
                return player
        return None

    def getPlayerByID(self, id=int):
        """Recherche un joueur en fonction de son id. L'id doit être un int. Renvois None si l'id n'est pas présent."""
        for player in self.Players:
            if str(player["id"]) == id:
                return player
        return None

    def getFirstPlayerByRole(self, role=str):
        """Recherche un joueur en fonction de son role. Le rôle doit être une string (ref. Roles.py). Renvois None si le rôle n'est pas présent."""
        for player in self.Players:
            if player["role"].name == role:
                return player
        return None

    def getPlayersByRole(self, role=str):
        """Recherche tout les joueurs avec un role défini. Le rôle doit être une string (ref. Roles.py). Renvois une liste vide si le rôle n'est pas présent."""
        role_list = list()
        for player in self.Players:
            if player["role"].name == role:
                role_list.append(player)
        return role_list
