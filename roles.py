import loup_garou

class Role:
    def __init__(self):
        self.name = "undefined"
        self.team = -1
        self.description = "undefined"
        self.alive = True

class Voyante(Role):
    def __init__(self):
        Role.__init__(self)
        self.name = "voyante"
        self.team = 1
        self.description = "La voyante peut connaître l'identité d'une personne qu'elle désigne par nuit.\nEquipe: \"villageois\""

class Villageois(Role):
    def __init__(self):
        Role.__init__(self)
        self.name = "villageois"
        self.team = 1
        self.description = "Le villageois se contente de dormir pendant la nuit. Son rôle est d'éliminer les loup-garou pendant le vote.\nEquipe: \"villageois\""

class Loup(Role):
    def __init__(self):
        Role.__init__(self)
        self.name = "loup-garou"
        self.team = 2
        self.description = "Les Loups-Garou ont pour but d'éliminer toutes l'équipe villageoise.\n\
                            Pour cela, une fois par nuit, les Loup désignent une personne à éliminer.\n\
                            Un autre moyen pour eux d'éliminer les villageois est de convaincre les autres joueurs de voter avec vous.\
                            Equipe: \"loups\""

class Cupidon(Role):
    def __init__(self):
        Role.__init__(self)
        self.name = "cupidon"
        self.team = 1
        self.description = "Le cupidon désigne 2 personnes au début du jeu qui seront amoureux.\n\
                            Leur priorité sera de se sauver l'un l'autre. Si un des amoureux meurt, l'autre le suit.\n\
                            Equipe: \"villageois\""
        self.Power = True

class Sorciere(Role):
    def __init__(self):
        Role.__init__(self)
        self.name = "sorcière"
        self.team = 1
        self.description = "La sorcière a le choix, pendant la nuit, d'utiliser une potion de vie ou de mort sur un joueur.\n\
                            Potion de vie: Sauve la vie de la personne désignée par les loups (1 utilisation).\n\
                            Potion de mort: Tue une personne (1 utilisation).\n\
                            Equipe: \"villageois\""
        self.LPotion = True
        self.DPotion = True

class Chasseur(Role):
    def __init__(self):
        Role.__init__(self)
        self.name = "chasseur"
        self.team = 1
        self.description = "Le chasseur désigne une personne lorsqu'il meurt. La personne désigné meurt à son tour.\n\
                            Equipe: \"villageois\""