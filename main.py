from discord.ext.commands import Bot
from discord.utils import get
import config
from loup_garou import LoupGarou


#Mentions: <@ID>


bot = Bot(command_prefix="!")

LoupGarou = LoupGarou(bot)


async def abortBot(ctx):
    """Stop le bot en nettoyant les serveurs"""
    await ctx.send("Le bot à rencontré une erreur. Il quitte le serveur... (abort)")
    taniere_channel = bot.get_guild(config.wolf_team).get_channel(config.wolf_team_channel)
    await taniere_channel.purge()
    print("Le bot à rencontré une erreur. Il quitte le serveur... (abort)")
    await bot.close()

def isNewGameMessage(message):
    return message.content == config.new_game_message and message.author.bot is True

async def closeTheGame():
    print("Fin de partie")
    taniere_channel = bot.get_guild(config.wolf_team).get_channel(config.wolf_team_channel)
    game_channel = bot.get_channel(config.game_channel)
    poll_channel = bot.get_channel(config.poll_channel)
    await taniere_channel.purge()
    await game_channel.purge()
    await poll_channel.purge(check=isNewGameMessage)
    LoupGarou.reset()



def checkForNewGameMessage(reaction):
    if reaction.message.content == config.new_game_message and reaction.message.author.bot == True:
        return True
    else:
        return False

async def send_link_to_wolves():
    """Envois une invitation à tout les loups-garou de la partie."""
    wolves = LoupGarou.getPlayersByRole("loup-garou")
    for wolf in wolves:
        link = await bot.get_guild(config.wolf_team).get_channel(config.wolf_team_channel).create_invite(max_age=300)
        await wolf["user"].send("Le lien du serveur dédié aux loup-garou: {}".format(link))


async def setting_up_wolves_privacy():
    """Mise en place du serveur privé des loups-garou."""
    taniere_channel = bot.get_guild(config.wolf_team).get_channel(config.wolf_team_channel)
    await taniere_channel.send("Vous avez tous été désigné loup-garou.\nIci vous pourrez communiquer sans qu'un joueur adverse ne soit notifié de vos messages.\n")
    await send_link_to_wolves()


async def newGamePollSystem(reaction, user):
    """Système de vote pour rejoindre une partie."""
    if reaction.count <= LoupGarou.maxPlayer + 1:
        if str(reaction.emoji) == "✅":
            if LoupGarou.addPlayer(user, user.id) is True:
                print("{} ajouté !".format(user))
            else:
                print("Un bot a essayé de rejoindre la partie")
        elif str(reaction.emoji) == "▶":
            if user.bot == True and user.id == config.bot_id:
                print("Boutton play initialisé")
            elif user.id != LoupGarou.gameChief.id:
                await reaction.remove(user)
                print("Réaction retiré (Un joueur random à essayé de lancer la partie)")
            else:
                await LoupGarou.startGame()
                await setting_up_wolves_privacy()
    else:
        await reaction.remove(user)
        print("Réaction retiré (trop de monde)")



async def setting_up_poll_new_game(ctx):
    """Mise en place du vote pour une nouvelle partie."""
    main_channel = bot.get_channel(config.poll_channel)
    message = await main_channel.send(config.new_game_message)
    await message.add_reaction('✅')
    await message.add_reaction('▶')
    LoupGarou.status = "Waiting for players"
    LoupGarou.gameChief = ctx.message.author
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
    if guild_id == config.wolf_team:
        print("Réaction depuis le serveur des loups !")
    else:
        print("Réaction depuis le serveur hôte !")
        await global_reaction(reaction, user)

@bot.event
async def on_reaction_remove(reaction, user):
    if checkForNewGameMessage(reaction) == True and reaction.count < config.max_player + 1:
        if str(reaction.emoji) == "✅":
            LoupGarou.removePlayer(user.id)
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
    if LoupGarou.status == "Out":
        await setting_up_poll_new_game(ctx)
    elif LoupGarou.status == "Waiting for players":
        await ctx.send("Une partie est déjà en attente de joueurs.\n")
    elif LoupGarou.status == "Playing":
        await ctx.send("La partie à déjà commencé...\nEssayes plus tard")

@bot.command()
async def closeGame(ctx):
    if LoupGarou.gameChief == None:
        await ctx.send("Aucune partie en cours...\nTu peux en lancer une en écrivant !newGame")
        print("Quelqu'un a essayé de fermer une partie inexistante")
        return
    if ctx.message.author.id == LoupGarou.gameChief.id:
        await closeTheGame()
    else:
        await ctx.send("Seul le chef de partie peut la fermer.")
        print("Quelqu'un a essayé de fermer une partie sans être l'hôte")

@bot.command()
async def invite(ctx, username):
    if LoupGarou.status == "Out":
        await ctx.send("Aucune partie n'a été lancé, ça ne sert à rien d'inviter quelqu'un.\nPour commencer une partie envoyez \"!newGame\".")
    elif (LoupGarou.status == "Playing"):
        await ctx.send("Une partie est déjà en cours. Personne ne peut rejoindre")
    else:
        users = bot.users
        users = [user for user in users if str(user.name + "#" + user.discriminator) == username]
        print("{} invité !".format(users[0]))
        await users[0].send("Go jouer au Loup Garou sur Discord !")


bot.run(config.token)