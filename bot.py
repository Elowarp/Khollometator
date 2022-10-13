import os
import discord
from discord.ext import commands
import khollometre
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
DEBUG = os.getenv("DEBUG")

Serv_id=883070060070064148 #Id du serveur où on écrit
Test_id=883633997740126249 #Id salon test
Annonce_id=939621805113626624 #Id du channel annonce


class Messager(commands.Bot):
    def __init__(self, debug):
        intents = discord.Intents.all()
        super().__init__(intents=intents, command_prefix="/")
        
        self.debug = debug
        self.collo = khollometre.Collometre(debug=self.debug)
        
        # Si on est en debug mode, on fait nos tests dans le channel test
        # et pas annonce
        if debug:
            self.channel_announce = Test_id
            
        else:
            self.channel_announce = Annonce_id


    async def on_ready(self):
        """
        Quand le bot est pret alors on lance une annonce dans le channel
        voulu, sert à debug, on changera après
        """
        print("Bot is ready, is debug mode ? : {}".format(self.debug))


    async def on_message(self, message):
        # Si on fait la commande weekannounce dans le channel Annonce mp2i
        if "weekannounce" in message.content \
            and message.channel.id == self.channel_announce:
            
            # On fait l'annonce dans le channel
            message = self.collo.weeklySummup().split("\n")
            part1 = "\n".join(message[:len(message)//3])
            part2 = "\n".join(message[(len(message)//3)+1:2*(len(message)//3)])
            part3 = "\n".join(message[2*len(message)//3+1:])
            await self.get_guild(Serv_id).get_channel(self.channel_announce).send(part1)
            await self.get_guild(Serv_id).get_channel(self.channel_announce).send(part2)
            await self.get_guild(Serv_id).get_channel(self.channel_announce).send(part3)
        
        elif message.content.split(" ")[0]=="ls" :
            if (message.content.split(" ")[1] and int(message.content.split(" ")[1]) > 0 ):
                await self.get_guild(Serv_id).get_channel(self.channel_announce).send("Tu as demandé le khollomètre de la semaine pour le groupe {}".format(int(message.content.split(" ")[1])))
                
if __name__ == "__main__":
    messager = Messager(debug=DEBUG)
    messager.run(TOKEN)
