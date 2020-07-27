from discord.ext.commands import Bot
import config
from loup_garou import Loup
import time

#Mentions: <@ID>


bot = Bot(command_prefix="!")

LoupGarou = Loup()

@bot.event
async def on_ready():
    print("Bot connected !")


def checkForNewGameMessage(reaction):
    if reaction.message.content == config.newGameMessage and reaction.message.author.bot == True:
        return True
    else:
        return False

@bot.event
async def on_reaction_add(reaction, user):
    if checkForNewGameMessage(reaction) == True:
        if reaction.count <= LoupGarou.maxPlayer:
            LoupGarou.addPlayer(str(user), user.id)
            print("{} ajouté !".format(user))
            await bot.get_channel(719177371714060288).send("<@{}>".format(user.id))
        else:
            await reaction.remove(user)
            print("Réaction retiré (trop de monde)")
    else:
        print("C'est pas le bon message !")

@bot.event
async def on_reaction_remove(reaction, user):
    if checkForNewGameMessage(reaction) == True and reaction.count < config.maxPlayer:
        LoupGarou.removePlayer(user.id)
        print("{} retiré !".format(user))
        

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
        await main_channel.send(config.newGameMessage)
        LoupGarou.status = "Waiting for players"
        LoupGarou.gameChief = ctx.message.author
        print("{} a commencé une partie ! ".format(ctx.message.author))
    elif LoupGarou.status == "Waiting for players":
        await ctx.send("Une partie est déjà en attente de joueurs.\n")
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
        print("{} invité !".format(users[0]))
        await users[0].send("Go jouer au Loup Garou sur Discord !")


bot.run(config.token)