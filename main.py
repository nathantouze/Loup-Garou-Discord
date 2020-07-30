from discord.ext import commands
import discord
import config
from app_data import appData
import random
#Mentions: <@ID>

bot = commands.Bot(command_prefix="!")

data = appData()


async def abortBot(channel):
    """Stop le bot en nettoyant les serveurs"""
    await channel.send("Le bot quitte le serveur...")
    await closeTheGame()
    print("Le bot quitte le serveur...")
    await bot.close()

def isNewGameMessage(message):
    return message.content == data.new_game_message and message.author.bot is True

async def closeTheGame():
    """Ferme la partie."""
    taniere_channel = bot.get_guild(data.server_wolf).get_channel(data.wolf_channel)
    game_channel = bot.get_channel(data.game_channel)
    poll_channel = bot.get_channel(data.poll_channel)
    player_liste = [player["user"] for player in data.game.players]

    print("Fin de partie")
    for player in player_liste:
        if player.id != data.server_wolf_owner and player.bot is False:
            await bot.get_guild(data.server_wolf).kick(player, reason="Fin de partie")
    if data.game.invite != None:
        await bot.delete_invite(data.game.invite)
    await taniere_channel.purge()
    if game_channel != None:
        await game_channel.delete(reason="Closing game")
    await poll_channel.purge(check=isNewGameMessage)
    data.game.reset()


async def pickup_new_chief():
    if data.game.players == []:
        await bot.get_channel(data.game_channel).send("Impossible de choisir un nouveau chef de game.\nLa partie se termine...")
        return
    newChief = random.choice(data.game.players)
    data.game.gameChief = newChief["user"]
    await bot.get_channel(data.game_channel).send("Le nouveau chef de game est <@{}>.".format(newChief["user"].id))

async def getResults():
    isVillager = False
    isWolf = False
    isLover = False

    if data.game.players == []:
        await closeTheGame()
        return isVillager, isWolf, isLover
    for player in data.game.players:
        if player["role"].team == 1 and player["role"].alive is True:
            isVillager = True
        elif player["role"].team == 2 and player["role"].alive is True:
            isWolf = True
        elif player["role"].team == 3 and player["role"].alive is True:
            isLover = True
        elif player["role"].alive is False:
            continue
        else:
            await closeTheGame()
            return isVillager, isWolf, isLover
    return isVillager, isWolf, isLover

async def printResults():
    """Affiche les résultats de la partie."""
    congrats = str()
    isVillager, isWolf, isLover = await getResults()

    if isVillager == False and isWolf is False and isLover is False:
        return
    if isWolf == isVillager and isLover is True:
        await bot.get_channel(data.game_channel).send("Les amoureux remportent la victoire !")
        return
    if isWolf is True:
        winner_list = [player for player in data.game.players if player["role"].name == "loup-garou"]
        congrats = "Félicitation "
        for player in winner_list:
            congrats += "<@{}> ".format(player["id"])
        await bot.get_channel(data.game_channel).send("Les loups remportent la victoire !\n" + congrats)
    if isVillager is True:
        winner_list = [player for player in data.game.players if player["role"].name != "loup-garou"]
        congrats = "Félicitation "
        for player in winner_list:
            congrats += "<@{}> ".format(player["id"])
        await bot.get_channel(data.game_channel).send("Les villageois remportent la victoire !\n" + congrats)
    if isLover is True:
        winner_list = [player for player in data.game.players if player["role"].team == 3]
        congrats = "Félicitation "
        for player in winner_list:
            congrats += "<@{}> ".format(player["id"])
        await bot.get_channel(data.game_channel).send("Les amoureux ont également remporté la victoire !\n" + congrats)


def checkForNewGameMessage(reaction):
    if reaction.message.content == data.new_game_message and reaction.message.author.bot == True:
        return True
    else:
        return False


async def reveal_roles(game_channel):
    for player in data.game.players:
        await game_channel.send("<@{}> est {}.".format(player["id"], player["role"].name))


async def add_role_to_players():
    server = bot.get_guild(data.server)
    overwrites = {
        server.default_role: discord.PermissionOverwrite(read_messages=False),
        server.me: discord.PermissionOverwrite(read_messages=True)
    }
    game_channel = await server.create_text_channel('loup-garou', overwrites=overwrites)
    data.game_channel = game_channel.id 
    for player in data.game.players:
        await game_channel.set_permissions(player["user"], read_messages=True, send_messages=False)
    await game_channel.send("La partie commence !")
    await reveal_roles(game_channel)


async def send_link_to_wolves():
    """Envois une invitation à tout les loups-garou de la partie."""
    wolves = data.game.getPlayersByRole("loup-garou")
    for wolf in wolves:
        data.game.invite = await bot.get_guild(data.server_wolf).get_channel(data.wolf_channel).create_invite(max_age=300)
        if wolf["user"].bot is False:
            await wolf["user"].send("Le lien du serveur dédié aux loup-garou: {}".format(data.game.invite))


async def setting_up_wolves_privacy():
    """Mise en place du serveur privé des loups-garou."""
    taniere_channel = bot.get_guild(data.server_wolf).get_channel(data.wolf_channel)
    await taniere_channel.send("Vous avez tous été désigné loup-garou.\nIci vous pourrez communiquer sans qu'un joueur adverse ne soit notifié de vos messages.\n")
    await send_link_to_wolves()


async def tellRoleToPlayers():
    for player in data.game.players:
        if player["user"].bot is False:
            await player["user"].send("Tu es " + player["role"].name + ".\n\n" + player["role"].description)

async def startGameRequest(reaction, user):
    if user.bot == True and user.id == config.bot_id:
        return
    elif user.id != data.game.gameChief.id:
        await reaction.remove(user)
        print("Réaction retiré: un joueur random a essayé de lancer la partie")
    elif user.id == data.game.gameChief.id and data.game.getPlayerByID(user.id) == None:
        await reaction.remove(user)
        print("Réaction retiré: le chef de game a voulu lancer la partie sans l'avoir rejoint.")
    else:
        data.game.startGame(data.game_channel)
        await tellRoleToPlayers()
        await add_role_to_players()
        await setting_up_wolves_privacy()


def addPlayerRequest(reaction, user):
    #if user.bot is True:
    #    return
    if user.bot is True and user.id == config.bot_id:
        pass
    else:
        data.game.addPlayer(user, user.id)

async def newGamePollSystem(reaction, user):
    """Système de vote pour rejoindre une partie."""
    if reaction.count <= data.max_player + 1:
        if str(reaction.emoji) == "✅":
            addPlayerRequest(reaction, user)
        elif str(reaction.emoji) == "▶":
            await startGameRequest(reaction, user)
    else:
        await reaction.remove(user)
        await reaction.message.channel.send("La partie a atteint sa limite de joueur.\n\
Elle est en attente de confirmation de la part de celui qui l'a démarrée.")



async def setting_up_poll_new_game(ctx):
    """Mise en place du vote pour une nouvelle partie."""
    main_channel = bot.get_channel(data.poll_channel)
    message = await main_channel.send(data.new_game_message)
    await message.add_reaction('✅')
    await message.add_reaction('▶')
    data.game.status = "Waiting for players"
    data.game.gameChief = ctx.message.author
    print("{} a commencé une partie ! ".format(ctx.message.author))



async def global_reaction(reaction, user):
    if checkForNewGameMessage(reaction) == True:
        await newGamePollSystem(reaction, user)
    else:
        print("Réaction ajouté sur une publication random")



@bot.event
async def on_ready():
    print("Bot connected !")



@bot.event
async def on_reaction_add(reaction, user):
    guild_id = reaction.message.guild.id
    if guild_id == data.server_wolf:
        print("Réaction depuis le serveur des loups !")
    else:
        print("Réaction depuis le serveur hôte !")
        await global_reaction(reaction, user)

@bot.event
async def on_reaction_remove(reaction, user):
    if checkForNewGameMessage(reaction) == True and reaction.count < data.max_player + 1:
        if str(reaction.emoji) == "✅" and user.bot is False:
            data.game.removePlayer(user.id)



@bot.command()
@commands.has_permissions(administrator=True)
async def exit(ctx):
    await abortBot(ctx)


@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount=100):
    await ctx.channel.purge(limit=amount)


@bot.command()
async def guild(ctx):
    await ctx.send("actual guild: " + ctx.guild.id)

@bot.command()
async def ping(ctx):
    await ctx.send("pong !")

@bot.command()
async def newGame(ctx):
    """Commence le poll pour rejoindre."""
    if data.game.status == "Out":
        await setting_up_poll_new_game(ctx)
    elif data.game.status == "Waiting for players":
        await ctx.send("Une partie est déjà en attente de joueurs.\n")
    elif data.game.status == "Playing":
        await ctx.send("La partie à déjà commencé...\nEssayes plus tard")


@bot.command()
async def leave(ctx):
    """Fait quitter le joueur si il est présent dans la partie."""
    if data.game.status != 'Playing':
        await ctx.send("Vous ne pouvez pas quitter une partie qui n'a pas commencé.")
        return
    player = data.game.getPlayerByID(ctx.message.author.id)
    if player == None:
        await ctx.send("Vous ne faite pas partie de la partie en cours. Impossible de la quitter.")
        return
    ret_rm = data.game.removePlayer(player["id"])
    if ret_rm is False:
        await bot.get_channel(data.poll_channel).send("Le bot a rencontré un erreur pendant la partie")
        await abortBot(bot.get_channel(data.poll_channel))
        return
    await bot.get_channel(data.game_channel).send("<@{}> à quitté. Il était {}.".format(player["id"], player["role"].name))
    if player["id"] == data.game.gameChief.id:
        await pickup_new_chief()
    if data.game.isOver() == True:
        await printResults()



@bot.command()
async def closeGame(ctx):
    """Ferme la partie. Seul le chef de game peut la fermer."""
    if data.game.gameChief == None:
        await ctx.send("Aucune partie en cours...\nTu peux en lancer une en écrivant !newGame")
        return
    if ctx.message.author.id == data.game.gameChief.id:
        await closeTheGame()
    else:
        await ctx.send("Seul le chef de game peut la fermer.")

@bot.command()
async def invite(ctx, username=""):
    """Invite un joueur en DM."""
    if data.game.status == "Out":
        await ctx.send("Aucune partie n'a été lancé, ça ne sert à rien d'inviter quelqu'un.\nPour commencer une partie envoyez \"!newGame\".")
    elif (data.game.status == "Playing"):
        await ctx.send("Une partie est déjà en cours. Personne ne peut rejoindre")
    else:
        users = bot.users
        invited_user = [user for user in users if str(user.name + "#" + user.discriminator) == username]
        if invited_user != [] and str(invited_user[0]) != bot.user.name + "#" + bot.user.discriminator:
            await invited_user[0].send("Go jouer au Loup Garou sur Discord !")
        elif username == "":
            await ctx.send("Il faut préciser le nom du joueur et son numéro comme ceci: " + bot.user.name + "#" + bot.user.discriminator + ".")
        else:
            await ctx.send("Le joueur spécifié n'a pas été trouvé. Le nom soit être de la forme \"*nom*#*numéro*\".")

bot.run(config.token)