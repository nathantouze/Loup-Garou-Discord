from discord.ext import commands
import discord
import config
from loup_garou import LoupGarou
#Mentions: <@ID>


class bot_data:
    def __init__(self, bot):
        self.game = LoupGarou(bot)
        self.game_channel = None
        self.server = config.server
        self.server_wolf = config.wolf_team
        self.wolf_channel = config.wolf_team_channel
        self.poll_channel = config.poll_channel
        self.max_player = config.max_player
        self.new_game_message = config.new_game_message


bot = commands.Bot(command_prefix="!")

data = bot_data(bot)


async def abortBot(ctx):
    """Stop le bot en nettoyant les serveurs"""
    await ctx.send("Le bot à rencontré une erreur. Il quitte le serveur... (abort)")
    taniere_channel = bot.get_guild(data.server_wolf).get_channel(data.wolf_channel)
    await taniere_channel.purge()
    print("Le bot à rencontré une erreur. Il quitte le serveur... (abort)")
    await bot.close()

def isNewGameMessage(message):
    return message.content == data.new_game_message and message.author.bot is True

async def closeTheGame():
    print("Fin de partie")
    taniere_channel = bot.get_guild(data.server_wolf).get_channel(data.wolf_channel)
    game_channel = bot.get_channel(data.game_channel)
    poll_channel = bot.get_channel(data.poll_channel)
    await taniere_channel.purge()
    await game_channel.delete(reason="Closing game")
    await poll_channel.purge(check=isNewGameMessage)
    data.game.reset()



def checkForNewGameMessage(reaction):
    if reaction.message.content == data.new_game_message and reaction.message.author.bot == True:
        return True
    else:
        return False


async def add_role_to_players():
    server = bot.get_guild(data.server)
    overwrites = {
        server.default_role: discord.PermissionOverwrite(read_messages=False),
        server.me: discord.PermissionOverwrite(read_messages=True)
    }
    game_channel = await server.create_text_channel('loup-garou', overwrites=overwrites)
    data.game_channel = game_channel.id 
    for player in data.game.Players:
        await game_channel.set_permissions(player["user"], read_messages=True, send_messages=False)
    await game_channel.send("La partie commence !")



async def send_link_to_wolves():
    """Envois une invitation à tout les loups-garou de la partie."""
    wolves = data.game.getPlayersByRole("loup-garou")
    for wolf in wolves:
        link = await bot.get_guild(data.server_wolf).get_channel(data.wolf_channel).create_invite(max_age=300)
        await wolf["user"].send("Le lien du serveur dédié aux loup-garou: {}".format(link))


async def setting_up_wolves_privacy():
    """Mise en place du serveur privé des loups-garou."""
    taniere_channel = bot.get_guild(data.server_wolf).get_channel(data.wolf_channel)
    await taniere_channel.send("Vous avez tous été désigné loup-garou.\nIci vous pourrez communiquer sans qu'un joueur adverse ne soit notifié de vos messages.\n")
    await send_link_to_wolves()


async def newGamePollSystem(reaction, user):
    """Système de vote pour rejoindre une partie."""
    if reaction.count <= data.max_player + 1:
        if str(reaction.emoji) == "✅":
            if data.game.addPlayer(user, user.id) is True:
                print("{} ajouté !".format(user))
            else:
                print("Un bot a essayé de rejoindre la partie")
        elif str(reaction.emoji) == "▶":
            if user.bot == True and user.id == config.bot_id:
                print("Boutton play initialisé")
            elif user.id != data.game.gameChief.id:
                await reaction.remove(user)
                print("Réaction retiré (Un joueur random à essayé de lancer la partie)")
            else:
                await data.game.startGame(data.game_channel)
                await add_role_to_players()
                await setting_up_wolves_privacy()
    else:
        await reaction.remove(user)
        print("Réaction retiré (trop de monde)")



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
        if str(reaction.emoji) == "✅":
            data.game.removePlayer(user.id)
            print("{} retiré !".format(user))



@bot.command()
async def abort(ctx):
    await abortBot(ctx)


@bot.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)


@bot.command()
async def guild(ctx):
    await ctx.send("actual guild: " + ctx.guild.id)

@bot.command()
async def ping(ctx):
    await ctx.send("pong !")

@bot.command()
async def newGame(ctx):
    if data.game.status == "Out":
        await setting_up_poll_new_game(ctx)
    elif data.game.status == "Waiting for players":
        await ctx.send("Une partie est déjà en attente de joueurs.\n")
    elif data.game.status == "Playing":
        await ctx.send("La partie à déjà commencé...\nEssayes plus tard")


@bot.command()
async def leave(ctx):
    if data.game.status != 'Playing':
        await ctx.send("Vous ne pouvez pas quitter une partie qui n'a pas commencé.")
    else:
        player = data.game.getPlayerByID(ctx.message.author.id)
        if player == None:
            await ctx.send("Vous ne faite pas partie de la partie en cours. Impossible de la quitter.")
            return
        else:
            ret_rm = data.game.removePlayer(player["id"])
            if ret_rm is False:
                await abortBot(ctx)
                return
            else:
                if data.game.isOver() == False:
                    await ctx.send("<@{}> à quitté. Il était {}.".format(player["id"], player["role"].name))
                







@bot.command()
async def closeGame(ctx):
    if data.game.gameChief == None:
        await ctx.send("Aucune partie en cours...\nTu peux en lancer une en écrivant !newGame")
        print("Quelqu'un a essayé de fermer une partie inexistante")
        return
    if ctx.message.author.id == data.game.gameChief.id:
        await closeTheGame()
    else:
        await ctx.send("Seul le chef de partie peut la fermer.")
        print("Quelqu'un a essayé de fermer une partie sans être l'hôte")

@bot.command()
async def invite(ctx, username):
    if data.game.status == "Out":
        await ctx.send("Aucune partie n'a été lancé, ça ne sert à rien d'inviter quelqu'un.\nPour commencer une partie envoyez \"!newGame\".")
    elif (data.game.status == "Playing"):
        await ctx.send("Une partie est déjà en cours. Personne ne peut rejoindre")
    else:
        users = bot.users
        users = [user for user in users if str(user.name + "#" + user.discriminator) == username]
        print("{} invité !".format(users[0]))
        await users[0].send("Go jouer au Loup Garou sur Discord !")


bot.run(config.token)