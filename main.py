from discord.ext.commands import Bot
import config
from loup_garou import LoupGarou
import time

#Mentions: <@ID>


bot = Bot(command_prefix="!")

LoupGarou = LoupGarou()

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
        if reaction.count <= LoupGarou.maxPlayer + 1:
            if str(reaction.emoji) == "✅":
                if LoupGarou.addPlayer(user, user.id) is True:
                    print("{} ajouté !".format(user))
                else:
                    print("Un bot a essayé de rejoindre la partie")
            elif str(reaction.emoji) == "▶":
                if user.bot == True and user.id == config.BotID:
                    print("Boutton play initialisé")
                elif user.id != LoupGarou.gameChief.id:
                    await reaction.remove(user)
                    print("Réaction retiré (Un joueur random à essayé de lancer la partie)")
                else:
                    LoupGarou.startGame()
        else:
            await reaction.remove(user)
            print("Réaction retiré (trop de monde)")
    else:
        print("Réaction ajouté sur une publication random")

@bot.event
async def on_reaction_remove(reaction, user):
    if checkForNewGameMessage(reaction) == True and reaction.count < config.maxPlayer + 1:
        if str(reaction.emoji) == "✅":
            LoupGarou.removePlayer(user.id)
            print("{} retiré !".format(user))




@bot.command()
async def ping(ctx):
    await ctx.send("pong !")

@bot.command()
async def newGame(ctx):
    if LoupGarou.status == "Out":
        main_channel = bot.get_channel(719177371714060288)
        message = await main_channel.send(config.newGameMessage)
        await message.add_reaction('✅')
        await message.add_reaction('▶')
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