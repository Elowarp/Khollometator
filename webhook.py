import requests
import os
import dotenv
import logging

from khollometre import Khollometre

# Récupération des variables d'environnement
dotenv.load_dotenv()
MP2I_webhook_url = os.getenv("MP2I_webhook_url")
MPI_webhook_url = os.getenv("MPI_webhook_url")


# Logging
LOG_FILENAME = "khollometre.log"
logging.basicConfig(format='%(asctime)s %(message)s', 
                    datefmt='%m/%d/%Y %H:%M:%S',
                    filename=LOG_FILENAME, level=logging.DEBUG)

# Constantes
ERROR_MESSAGE = ":warning: __Il y a un problème avec le khollomètre !__ Veuillez prévenir **<@240850328180883457>** !"


def send_message(message, url=MP2I_webhook_url):
    """
    Envoie un message sur le channel Discord
    """
    data = {"content": message}
    requests.post(url=url, json=data, 
                  headers={"Content-Type": "application/json"})


if __name__ == "__main__":
    logging.info("--- Starting khollometre ---")
    kholloMP2I = Khollometre(classe="MP2I", file="MP2I.csv", debug=False)
    kholloMPI = Khollometre(classe="MPI", file="MPI.csv", debug=False)


    # Récupération des messages
    try:
        messagesMP2I = kholloMP2I.weeklySummup()

    except Exception as e:
        messagesMP2I = [ERROR_MESSAGE]
        logging.error("MP2I ERROR")
        logging.exception(e)

    try:
        messagesMPI = kholloMPI.weeklySummup()

    except Exception as e:
        messagesMPI = [ERROR_MESSAGE]
        logging.error("MPI ERROR")
        logging.exception(e)


    # Envoie des messages
    logging.info("Sending messages")
    for message in messagesMP2I:
        send_message(message, url=MP2I_webhook_url)

    for message in messagesMPI:
        send_message(message, url=MPI_webhook_url)

    logging.info("--- Job Done ---")