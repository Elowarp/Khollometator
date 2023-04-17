import discord
from discord.ext import class_commands, commands
import khollometre
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
DEBUG = os.getenv("DEBUG")

Serv_id=883070060070064148              #Id du serveur où on écrit
Test_id=883633997740126249              #Id salon test
AnnonceMP2I_id=1031209793047761010      #Id du channel annonce MP2I
AnnonceMPI_id=1031209511383470160       #Id du channel annonce MP2I
AnnonceMPI_Bonus_id=1064209861220507718 #Id du channel annonce MPI Kholle bonus

client = discord.Client(intents=discord.Intents.default())
tree = discord.app_commands.CommandTree(client)

@client.event
async def setup_hook():
    await tree.sync()

class Ping(class_commands.SlashCommand):
    async def callback(self):
        await self.send(f'Pong!')

class khollotime(class_commands.SlashCommand):
    def __init__(self):
        self.debug = True if DEBUG == "True" else False
        self.messager = Messager(self.debug)

    async def callback(self, week:str=None, debug:str=None):
        status = "Kholling by now (By Elowarp)" if not self.debug else "DEBUG MODE"
        await client.change_presence(activity=discord.Game(name=status))

        # On récupère les paramètres de la commande
        try:
            params = self.interaction.data["options"]
            if params[0]["name"] == "week": week = params[0]["value"]
            else: 
                week = "None"
                debug = params[0]["value"]

        except IndexError: pass

        except KeyError: pass

        else:
            try:
                if params[1]["name"] == "debug": debug = params[1]["value"]
                else:
                    debug = "None"
                    week = params[1]["value"]

            except IndexError: pass
            except KeyError: pass

        if week != "None":
            # Assignation de la date aux khollomètres pour obtenir les bonnes données
            self.messager.khollometreMP2I.set_week(week)
            #self.messager.khollometreMPI.set_week(week)     
        
        else:
            # Mise à jour de la semaine de kholle voulue
            self.khollometreMP2I.update_date()
            #self.khollometreMPI.update_date()

        # Récupération des messages
        MP2Imessages = self.messager.messageMP2I()
        #MPImessages = self.messager.messageMPI()
        # kholleBonus = self.messager.messageMPI_Bonus()

        try:
            await self.send("Attention ça arrive !")

        except Exception: # Erreur du à la bibliothèque discord slash commands
            pass

        # Envoie de tous les messages
        announce_channel = Test_id if self.debug or debug else AnnonceMP2I_id
        for i in range(len(MP2Imessages)):
            await client.get_guild(Serv_id).get_channel(announce_channel).send(MP2Imessages[i])

        # announce_channel = Test_id if self.debug or debug else AnnonceMPI_id
        # for i in range(len(MPImessages)):
        #     await self.get_guild(Serv_id).get_channel(announce_channel).send(MPImessages[i])

        # announce_channel = Test_id if self.debug or debug else AnnonceMPI_Bonus_id
        # for i in range(len(kholleBonus)):
        #     await self.get_guild(Serv_id).get_thread(announce_channel).send(kholleBonus[i])     

class Messager():
    Groups_Bonus_Kholle=[4, 7, 10]          #Liste des groupes qui ont un kholle bonus  

    def __init__(self, debug):        
        # Définission du mode debug ou non en fonction du .env
        self.debug = debug

        self.khollometreMP2I = khollometre.Collometre(classe="MP2I", file="MP2I.xls", debug=self.debug)
        self.khollometreMPI = khollometre.Collometre(classe="MPI", file="MPI.xls", debug=self.debug)

    async def messageEveryone(self, week:str=None, debug:str=None):
        """
        Fonction envoyant le khollomètre dans le channel annonce de tout le monde
        """
        # Si on est en mode debug alors qu'on ne doit pas
        # on passe le mode debug à False
        # (c'est pour annuler le "debug" dans la commande d'avant
        # si jamais)
        if self.debug and DEBUG != "True":
            self.debug = False
        
        if debug != "true":
            self.debug = True

        await self.messageMP2I()
        await self.messageMPI()
        await self.messageMPI_Bonus()

    def messageMP2I(self):
        """
        Fonction envoyant le khollomètre dans le channel annonce des MP2I
        """
        return self.khollometreMP2I.weeklySummup()

    def messageMPI(self):
        """
        Fonction envoyant le khollomètre dans le channel annonce des MPI
        """
        return self.khollometreMPI.weeklySummup()

    def messageMPI_Bonus(self):
        """
        Fonction envoyant le khollomètre dans le channel annonce des MPI
        pour les kholles bonus
        """
        # On fait l'annonce dans le channel
        messages = self.khollometreMPI.weeklySummup()

        # Récupération des messages des groupes concernés
        list_messages = [
            "Pour vous, en __live__ et en __stéréo__, **les kholles bonus** : "
        ] # Message d'introduction

        # Message des groupes concernés
        for i in range(len(self.Groups_Bonus_Kholle)):
            list_messages.append(messages[self.Groups_Bonus_Kholle[i]])

        list_messages.append(messages[len(messages)-1])   # Message d'avertissement sur Noyer

        return list_messages

if __name__ == "__main__":
    print("Is debug ? {}".format(DEBUG))
    tree.add_command(Ping)
    tree.add_command(khollotime)
    client.run(TOKEN)
