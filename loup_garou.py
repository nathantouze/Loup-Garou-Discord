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

    async def startGame(self):
        self.status = "Playing"
        construct_plan = list(config.roles_per_players[self.nbPlayer])
        index = 0
        while self.checkGameInit(construct_plan) is False and index < self.nbPlayer:
            role = random.choice(construct_plan)
            print(role)
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
            await self.client.get_user(self.Players[index]["id"]).send("Tu es " + self.Players[index]["role"].name + "\n" + self.Players[index]["role"].description)
            construct_plan.remove(role)
            index += 1
        await self.client.get_channel(config.game_channel_id).send()
        

    def checkUsernames(self, username):
        for player in self.Players:
            if player["username"] == str(username):
                return False
        return True
    

    def addPlayer(self, username, id):
        """Ajoute un joueur si il n'est pas encore dedans. Renvois False en cas d'erreur"""
        if self.Players != [] and self.checkUsernames(username) is False:
            return False
        if username.bot is True:
            return False
        self.Players.append({"username":str(username), "id":id, "role":None})
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