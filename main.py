from discord.ext.commands import Bot
import config
from loup_garou import Loup

bot = Bot(command_prefix="!")

LoupGarou = Loup()

@bot.event
async def on_ready():
    print("Bot connected !")

@bot.command()
async def ping(ctx):
    await ctx.send("pong !")

@bot.command()
async def servInfo(ctx):
    if str(ctx.message.author).endswith("#1524"):
        server = ctx.guild
        numberOfTextChannels = len(server.text_channels)
        numberOfVoiceChannels = len(server.voice_channels)
        serverDescription = server.description
        numberOfPerson = server.member_count
        serverName = server.name
        await ctx.send("Le server {} contient {} personnes.\nDescription: {}\nCe server possède {} channels textuels et {} channels vocaux.".format(serverName, numberOfPerson, serverDescription, numberOfTextChannels, numberOfVoiceChannels))


@bot.command()
async def newGame(ctx):
    if LoupGarou.status == "Out":
        main_channel = bot.get_channel(719177371714060288)
        await main_channel.send("**" + str(ctx.message.author) + "** a commencé une partie.\n" + \
                                "Rejoignez la partie en écrivant \"!join\" ou invitez des joueurs en écrivant \"!invite [joueur]\"")
        LoupGarou.status = "Waiting for players"
        print("{} started a game !".format(ctx.message.author))
    elif LoupGarou.status == "Waiting for players":
        await ctx.send("Une partie est déjà en attente de joueurs.\nIl y a actuellement {}/{} joueurs dans la partie.\n".format(LoupGarou.nbPlayer, LoupGarou.maxPlayer)\
                    + "Tu peux la rejoindre en écrivant \"!join\".")
    elif LoupGarou.status == "Playing":
        await ctx.send("La partie à déjà commencé...\nEssayes plus tard")

@bot.command()
async def invite(ctx, username):
    if LoupGarou.status == "Out":
        await ctx.send("Aucune partie n'a été lancé, ça ne sert à rien d'inviter quelqu'un.\nPour commencer une partie envoyez \"!newGame\".")
    elif (LoupGarou.status == "Playing"):
        await ctx.send("Une partie est déjà en cours. Personne ne peut rejoindre")
    else:
        users = bot.users
        users = [user for user in users if str(user.name + "#" + user.discriminator) == username]
        print("{} invited !".format(users[0]))
        await users[0].send("Go jouer au Loup Garou sur Discord ! (**!join**)")

@bot.command()
async def join(ctx):
    if LoupGarou.status == "Out":
        await ctx.send("Aucune partie n'a été lancé\nPour commencer une partie envoyez \"!newGame\".")
    elif LoupGarou.status == "Playing":
        await ctx.send("Une partie est déjà en cours. Personne ne peut rejoindre")
    else:
        LoupGarou.addPlayer(str(ctx.author))
        await ctx.send("Vous avez rejoint la partie.")
        print(str(ctx.author) + " a rejoint la partie !")

@bot.command()
async def unjoin(ctx):
    if LoupGarou.status == "Out":
        await ctx.send("Aucune partie n'a été lancé\nPour commencer une partie envoyez \"!newGame\".")
    elif LoupGarou.status == "Playing":
        await ctx.send("Une partie est déjà en cours. Il n'y a plus de file d'attente")
    else:
        LoupGarou.removePlayer(str(ctx.author))
        print(str(ctx.author) + " a quitté la file d'attente !")
        await ctx.send("Vous avez quitté la partie !")



bot.run(config.token)