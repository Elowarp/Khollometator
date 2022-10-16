import os
import discord
from discord.ext import commands
import khollometre
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
DEBUG = os.getenv("DEBUG")


class Messager(commands.Bot):
    Serv_id=883070060070064148 #Id du serveur où on écrit
    Test_id=883633997740126249 #Id salon test
    AnnonceMP2I_id=939621805113626624 #Id du channel annonce MP2I
    AnnonceMPI_id=883104717872435242 #Id du channel annonce MP2I

    def __init__(self, debug):
        intents = discord.Intents.all()
        super().__init__(intents=intents, command_prefix="/")
        
        # Définission du mode debug ou non en fonction du .env
        self.debug = True if debug == "True" else False

        self.khollometreMP2I = khollometre.Collometre(classMention="939402771558441000", file="MP2I.xls", debug=self.debug)
        self.khollometreMPI = khollometre.Collometre(classMention="939403004698836992", file="MPI.xls", debug=self.debug)


    async def on_ready(self):
        """
        Quand le bot est pret alors on lance une annonce dans le channel
        voulu, sert à debug, on changera après
        """
        print("Bot is ready, is debug mode ? : {}".format(self.debug))
        await self.change_presence(activity=discord.Game(name="https://github.com/Elowarp/Kollometator  by LOGIC & Elowarp"))


    async def on_message(self, message):
        """
        Quand le bot détecte un message du serveur, il regarde le channel 
        et si c'est une commande connue, si c'est le cas, il exécute le 
        programme correspondant (soit envoyer une annonce de kholle)
        """
        # Si on fait la commande weekannounce dans le channel test
        # On envoie un message aux MPI et MP2I
        if "weekannounce" in message.content \
            and message.channel.id == self.Test_id:
            
            await self.messageMP2I()
            await self.messageMPI()
        
        """elif message.content.split(" ")[0]=="ls" :
            if (message.content.split(" ")[1] and int(message.content.split(" ")[1]) > 0 ):
                await self.get_guild(Serv_id).get_channel(self.channel_announce).send("Tu as demandé le khollomètre de la semaine pour le groupe {}".format(int(message.content.split(" ")[1])))"""
                

    async def messageMP2I(self):
        """
        Fonction envoyant le khollomètre dans le channel annonce des MP2I
        """
        # Si debug mode alors c'est le channel test, sinon cest le channel mp2i
        announce_channel = self.Test_id if self.debug else self.AnnonceMP2I_id

        # On fait l'annonce dans le channel
        messages = self.splitMessage(self.khollometreMP2I.weeklySummup())

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
        messages = self.splitMessage(self.khollometreMPI.weeklySummup())

        # On envoie un message pour chaque élément du tuple
        for i in range(len(messages)):
            await self.get_guild(self.Serv_id).get_channel(announce_channel).send(messages[i])
            

    def splitMessage(self, message):
        """
        Decoupe un message donné en plusieurs parties pour pouvoir être envoyé sur discord sans problème.

        Parameter: message(String) - Message à découper
        Returns: tuple - Tuple contenant les différents messages
        """

        # Création d'une liste découpée selon les retours chariots
        messages = message.split("\n")

        part1 = "\n".join(messages[:len(messages)//3])
        part2 = "\n".join(messages[(len(messages)//3):2*(len(messages)//3)])
        part3 = "\n".join(messages[2*len(messages)//3:])

        return (part1, part2, part3)


if __name__ == "__main__":
    messager = Messager(debug=DEBUG)
    messager.run(TOKEN)
