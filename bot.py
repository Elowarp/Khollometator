import os
import discord
from discord import app_commands
from discord.ext import commands
import khollometre
from dotenv import load_dotenv
import gc

load_dotenv()

TOKEN = os.getenv("TOKEN")
DEBUG = os.getenv("DEBUG")


class Messager(commands.Bot):
    Serv_id=883070060070064148              #Id du serveur où on écrit
    Test_id=883633997740126249              #Id salon test
    AnnonceMP2I_id=1031209793047761010      #Id du channel annonce MP2I
    AnnonceMPI_id=1031209511383470160       #Id du channel annonce MP2I
    AnnonceMPI_Bonus_id=1064209861220507718 #Id du channel annonce MPI Kholle bonus
    Groups_Bonus_Kholle=[4, 7, 10]          #Liste des groupes qui ont un kholle bonus  

    def __init__(self, debug):
        intents = discord.Intents.all()
        super().__init__(intents=intents, command_prefix="/")
        
        # Définission du mode debug ou non en fonction du .env
        self.debug = True if debug == "True" else False


        self.khollometreMP2I = khollometre.Collometre(classe="MP2I", file="MP2I.xls", debug=self.debug)
        self.khollometreMPI = khollometre.Collometre(classe="MPI", file="MPI.xls", debug=self.debug)

    async def on_ready(self):
        """
        Quand le bot est pret alors on lance une annonce dans le channel
        voulu, sert à debug, on changera après
        """
        self.tree.add_command(self.messageEveryone)
        self.add_command(sync)
        self.tree.copy_global_to(guild=discord.Object(id=self.Serv_id))

        print("Bot is ready, is debug mode ? : {}".format(self.debug))  
        status = "https://github.com/Elowarp/Kollometator  by LOGIC & Elowarp"

        if self.debug:
            status = "DEBUG MODE"

        await self.change_presence(activity=discord.Game(name=status))

    @app_commands.command(name = "khollotime", 
        description = "Envoyer les kholles à toutes les classes")
    async def messageEveryone(self, interaction, week:str=None, debug:str=None):
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

        if week != "None":
            # Assignation de la date aux khollomètres pour obtenir les bonnes données
            self.khollometreMP2I.set_week(week)
            self.khollometreMPI.set_week(week)     
        
        else:
            # Mise à jour de la semaine de kholle voulue
            self.khollometreMP2I.update_date()
            self.khollometreMPI.update_date()

        await self.messageMP2I()
        await self.messageMPI()
        await self.messageMPI_Bonus()

    async def messageMP2I(self):
        """
        Fonction envoyant le khollomètre dans le channel annonce des MP2I
        """
        # Si debug mode alors c'est le channel test, sinon cest le channel mp2i
        announce_channel = self.Test_id if self.debug else self.AnnonceMP2I_id

        # On fait l'annonce dans le channel
        messages = self.khollometreMP2I.weeklySummup()

        # On envoie un message pour chaque élément du tuple
        for i in range(len(messages)):
            await self.get_guild(self.Serv_id).get_channel(announce_channel).send(messages[i])

    async def messageMPI(self):
        """
        Fonction envoyant le khollomètre dans le channel annonce des MPI
        """
        # Si debug mode alors c'est le channel test, sinon cest le channel mpi
        announce_channel = self.Test_id if self.debug else self.AnnonceMPI_id

        # On fait l'annonce dans le channel
        messages = self.khollometreMPI.weeklySummup()

        # On envoie un message pour chaque élément du tuple
        for i in range(len(messages)):
            await self.get_guild(self.Serv_id).get_channel(announce_channel).send(messages[i])

    async def messageMPI_Bonus(self):
        """
        Fonction envoyant le khollomètre dans le channel annonce des MPI
        pour les kholles bonus
        """
        # Si debug mode alors c'est le channel test, sinon cest le channel mpi
        announce_channel = self.Test_id if self.debug else self.AnnonceMPI_Bonus_id

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

        # On envoie un message pour chaque élément du tuple
        for i in range(len(list_messages)):
            await self.get_guild(self.Serv_id).get_thread(announce_channel).send(list_messages[i])


@commands.command(name="sync")
async def sync(self, interaction: discord.Interaction=None):
    print("syncing commands...")
    messager = None
    
    for obj in gc.get_objects():
        if isinstance(obj, Messager):
            messager = obj

    app_commands.CommandTree.clear_commands(self, guild=discord.Object(id=Messager.Serv_id))
    await commands.CommandTree.sync()
    print("adding commands")
    app_commands.CommandTree.add_command(messager.messageEveryone)
    await app_commands.CommandTree.sync()
    print("commands synced")

if __name__ == "__main__":
    messager = Messager(debug=DEBUG)
    messager.run(TOKEN)