from calendar import weekday
from datetime import date, datetime, timedelta
import csv

import logging

# Logging
LOG_FILENAME = "khollometre.log"
logging.basicConfig(format='%(asctime)s %(message)s', 
                    datefmt='%m/%d/%Y %H:%M:%S',
                    filename=LOG_FILENAME, level=logging.DEBUG)

class Khollometre:
    def __init__(self, classe="MP2I", file="MP2I.csv", debug=True):
        # Défini si on est en production ou non
        self.debug = debug
    
        # Récupération des informations depuis le fichier csv
        with open(file, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            self.kholles = list(reader)


        # Dictionnaire contenant toutes les infos des kholles triées par groupe
        # Structuration :
        # {
        #   "4": #Numéro du groupe
        #       [
        #           {
        #               name : "Nom du prof",
        #               infos : "email",
        #               subject: "Physique",
        #               horaries: "Me 12-13",
        #               class: "S300",
        #               frGroup: "a" # Lettre correspondant à celui qui passe en fr
        #           }
        #       ]        
        # }
        self.khollesByGroup = {}

        # Variable contenant la classe sur laquelle on travaille
        self.classe = classe

        # Variable qui contient la semaine sur laquelle on travaille
        self.week = self._get_current_week()

        # Récupération des id des étudiants et de leurs groupes
        self.students = self._get_students_id_and_groups_from_csv(file="pings.csv")

    def update_date(self):
        """
        Fonction qui met à jour la date de la semaine sur laquelle on travaille

        Parameters : None
        Returns : None
        """

        self.week = self._get_current_week()

    def _get_students_id_and_groups_from_csv(self, file="pings.csv") -> dict:
        """
        Fonction qui récupère les groupes et les id des étudiants
        depuis le fichier excel pings.csv

        Parameters : None
        Returns : dict - Dictionnaire contenant les groupes et les 
                         id des étudiants
        """
        # Récupération des informations depuis le fichier excel
        with open(file, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            students = list(reader)

        # Stockage des id en fonction du groupe de kholle
        groups = {
            # groupNumber : [id1, id2, id3, ...],
        }

        # On parcourt les étudiants
        for student in students:
            # On récupère le groupe de l'étudiant
            group = int(student["Groupe"])

            # Si l'étudiant n'est pas dans la classe, 
            # on passe à l'étudiant suivant
            if student["Classe"] != self.classe:
                continue

            # Si le groupe n'existe pas dans le dictionnaire, on l'ajoute
            if group not in groups:
                groups[group] = []

            # On ajoute l'id de l'étudiant dans le groupe correspondant
            groups[group].append(int(student["ID"]))

        return groups

    def _get_current_week(self) -> int:
        """
        Récupère le lundi de la semaine prochaine et le renvoie sous
        la forme jj-mm

        Parameters: None
        
        Returns: String
        """
        # Récupération du jour d'aujourd'hui et calcule du nb de jours
        # restant jusque le prochain lundi 
        today = date.today()
        days_ahead = 0 - today.weekday()

        if days_ahead <= 0: # Target day already happened this week
            days_ahead += 7


        # Ajout du nb de jours restant avant le prochain lundi et du jour 
        # d'aujourd'hui afin d'obtenir une date, et convertion de la date
        # sous format : jj-mm (comme le Khollomètre)
        nextMonday = today + timedelta(days_ahead)
        nextMondayString = nextMonday.strftime("%d-%m")

        return nextMondayString

    def set_week(self, week):
        """
        Permet de changer la semaine sur laquelle on travaille

        Parameters : week (String) : La semaine sous format jj-mm
        Returns : None
        """
        self.week = week   

    def _add_kholle_info_to_group(self, line) -> None:
        """
        Ajout des informations d'une ligne dans le dictionnaire d'informations

        Parameters:
            line (int): Ligne que l'on traite

        Returns : None
        """
        subject     = line["Matière"]
        teacher     = line["Kholleur/se"]
        horaries    = line["Créneaux"]
        classe      = line["Salles"]
        group       = line[self.week]
        frGroup     = None

        # Si le kholleur n'a pas de kholle cette semaine, 
        # on passe à la suivante
        if group == "":
            return None
        
        # On essaye de convertir le groupe en entier
        try:
            group = int(group)
        
        # Si on ne peut pas, c'est qu'on essaye de convertir "5 a" en entier 
        # or c'est impossible car illogique
        except ValueError:
            # Donc on découpe le string en deux au niveau de l'espace
            groupInfo = group.split(" ")

            # Et on attribu le chiffre au nom de groupe et la lettre
            # au frGroup (='a' ou 'b' ou 'c')
            frGroup = groupInfo[1]
            group = int(groupInfo[0])

        except Exception as e:
            logging.error("Erreur lors de la conversion du groupe en entier")
            logging.exception(e)
            return None
        
        # Si le groupe de kholle n'a toujours pas été ajouté au dico
        if group not in self.khollesByGroup:
            self.khollesByGroup[group] = []

        kholleInfos = {
            "subject": subject,
            "teacher": teacher,
            "horaries": horaries,
            "class": classe,
            "frGroup": frGroup
        }

        # Ajout des infos dans le tableau
        self.khollesByGroup[group].append(kholleInfos)

    def sort_kholles(self):
        """
        Fonction qui trie le dictionnaire de kholle pour qu'il
        soit dans l'ordre des groupes quand on le parcourt

        Parameters : None
        Returns : None 
        """
        # Triage du dictionnaire pour avoir un ordre 
        self.khollesByGroup = dict(sorted(self.khollesByGroup.items(), 
            key=lambda key: key))

    def _convert_datetime_to_timestamp(self, date) -> tuple:
        """
        Fonction qui prend un string d'une date de la forme Jj hh-hh 
        (ex: Lu 12-13) et retourne un tuple avec des timestamps correspondants
        au début puis la fin de l'heure voulue
        
        parameter: date(string) - Date sous format "Jj hh-hh"
        
        return: tuple - Sour format (timestamp debut heure, timestamp fin heure)
        """
        # Constantes utiles
        nbSecondsInHour = 60 * 60
        nbSecondsInDay = nbSecondsInHour * 24
        days = {"Di" : 6, "Lu": 0, "Ma": 1, "Me": 2, "Je": 3, "Ve": 4, "Sa": 5}

        # On récupère la date du prochain lundi et on ajoute l'année pour avoir
        # le format : "07-10-2022"
        nextMonday = self.week + "-" + str(datetime.today().year)
        
        # Convertion en format datetime d'un format "07-10-2022"
        nextMondayTimestamp = datetime.strptime(nextMonday, "%d-%m-%Y")
        
        # Découpage de la date donnée pour avoir ["Lu", "12-13"]
        date = date.split(" ")

        # Si on a une date au format "12h10", on préfèrera donnée le
        # timestamp avec les minutes piles
        if "h" in date[1]:
            minutes = int(date[1].split("h")[1]) * 60

            # On prend le timestamp du premier lundi de la semaine, on lui
            # ajoute le nb de jours correspondant pour atteindre le jour voulu
            # et ainsi pour l'heure et les minutes
            firstDate = nextMondayTimestamp.timestamp() + days[date[0]]\
                * nbSecondsInDay + int(date[1].split("h")[0])*nbSecondsInHour\
                + minutes
            
            secondDate = nextMondayTimestamp.timestamp() + days[date[0]]\
                * nbSecondsInDay + int(date[1].split("h")[1])*nbSecondsInHour\
                + minutes

        else:
            # On prend le timestamp du premier lundi de la semaine, on lui
            # ajoute le nb de jours correspondant pour atteindre le jour voulu
            # et ainsi pour l'heure
            firstDate = nextMondayTimestamp.timestamp() + days[date[0]]\
                * nbSecondsInDay + int(date[1].split("-")[0])*nbSecondsInHour 
            secondDate = nextMondayTimestamp.timestamp() + days[date[0]]\
                * nbSecondsInDay + int(date[1].split("-")[1])*nbSecondsInHour

        # Tuple contenant le debut de l'heure et la fin de l'heure
        return (int(firstDate), int(secondDate))

    def set_debug(self, debug):
        """
        Fonction qui permet de changer le mode debug

        Parameters : debug (bool)
        Returns : None
        """
        self.debug = debug

    def weeklySummup(self) -> list:
        """
        Fonction qui retourne le message à afficher aux élèves 
        sous forme de liste de phrases/blocs à afficher

        Parameters : None
        Returns : list
        """
        # Mise à jour des informations
        self.main()
        
        finalMessage = [
            "wsh les prépas, c'est l'heure du khollomètre de la semaine du **{}** WOUHOU\n".format(self.week)
        ]

        # Triage des kholles selon l'ordre croissant des groupes
        self.sort_kholles()

        # Parcours de tous les groupes déjà triés
        for group, colles in self.khollesByGroup.items():
            currentGroupMessage = "<:e:999621115406205029> **Groupe {}** : ".format(group)

            # Ajout des mentions des personnes du groupe sous forme 
            # "@machin @truc" s'il y a bien des personnes à mentionner
            if group in self.students and not self.debug:
                groupTags = "".join(["<@{}> ".format(self.students[group][i]) 
                    for i in range(len(self.students[group]))])

                currentGroupMessage += groupTags 

            currentGroupMessage += "\n"

            # Création d'un message pour chaque colle du groupe actuel
            for i in range(len(colles)): 
                # Mise en forme, ajout d'un espace au debut du message
                currentGroupMessage += "> • "
                
                currentGroupMessage += "`{}` : <t:{}:F> en __{}__ avec {}".format(
                    colles[i]["subject"], self._convert_datetime_to_timestamp(
                        colles[i]["horaries"])[0], colles[i]["class"], 
                        colles[i]["teacher"]
                    )

                # Si c'est une colle de fr, alors il y a des infos sur la lettre
                # qui passe, donc on peut l'ajouter au message
                if colles[i]["frGroup"] != None:
                    currentGroupMessage += " pour la lettre {}".format(colles[i]["frGroup"])

                currentGroupMessage += "\n"

                # Si on est à la dernière colle du groupe, on ajoute un saut de ligne vide
                if i == len(colles) - 1:
                    currentGroupMessage += "_ _"

            finalMessage.append(currentGroupMessage)

        finalMessage.append("⚠️ Coquilles possibles ! *(comme M.Noyer avec ses transparents)*")
        return finalMessage

    def main(self) -> None:
        """
        Fonction principale du programme

        Parameters : None
        Returns : None
        """        
        self.khollesByGroup = {} # Reset des kholles

        for line in self.kholles:
            self._add_kholle_info_to_group(line)


if __name__ == "__main__":
    collometrique = Khollometre(classe="MP2I", file="MP2I.csv", debug=False)
    collometrique.set_week("05-02")
    print(collometrique.weeklySummup())
