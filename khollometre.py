from calendar import weekday
from datetime import date, datetime, timedelta
import xlrd

class Collometre:

    def __init__(self, classMention="939402771558441000", file="MP2I.xls", debug=True):
        # Défini si on est en production ou non
        self.debug = debug

        # Définition de l'id de la classe(rôle) à qui on va faire le ping
        self.classMention = classMention
    
        # Récupération des informations depuis le fichier excel
        self.doc=xlrd.open_workbook(file)
        self.colles = self.doc.sheet_by_index(0)

        # Zone où se trouvent tout les groupes de kholles
        self.firstGroupCell = (2, 5)
        self.lastGroupCell = (self.colles.nrows - 1, self.colles.ncols - 1)

        # Les numéros des colonnes qui contiennent les différentes informations
        self.subjectsColumn = 0
        self.teachersColumn = 1
        self.infosColumn = 2
        self.horariesColumn = 3
        self.classColumn = 4


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
        #               frGroup: "" # Lettre correspondant à celui qui passe en fr
        #           }
        #       ]        
        # }
        self.khollesByGroup = {}

    def _get_current_week(self) -> int:
        """
        Récupère le lundi de la semaine prochaine et le renvoie sout forme jj-mm

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
        

    def _get_column_from_week(self) -> int:
        """
        Récupère la date du prochain lundi et renvoie l'index de la colonne
        correspondante à cette semaine
        """

        nextMonday = self._get_current_week()

        # On a colles[1] car la ligne des dates est la 2nd ligne donc pas 
        # besoin de parcourir tout le tableau
        for idColonne in range(len(self.colles[1])):
            if str(self.colles[1][idColonne].value) == nextMonday:
                return idColonne

    def _add_kholle_info_to_group(self, line, weekColumn) -> None:
        """
        Ajout des informations d'une ligne dans le dictionnaire d'informations

        Parameters:
            line (int): Ligne que l'on traite
            weekColumn (int) : Colonne de la semaine actuelle

        Returns : None
        """
        subject = str(self.colles[line, self.subjectsColumn].value)
        teacher = str(self.colles[line, self.teachersColumn].value)
        infos = str(self.colles[line, self.infosColumn].value)
        horaries = str(self.colles[line, self.horariesColumn].value)
        classe = str(self.colles[line, self.classColumn].value)
        group = self.colles[line, weekColumn].value
        frGroup = None

        # Si on a un saut de ligne dans le fichier
        if group == "": return

        # Distingo entre le nom de groupe "5" et "5 a"
        try:
            # On essaye de convertir "5" en int
            group = int(group)
        
        # Si on ne peut pas, c'est qu'on essaye de convertir "5 a" en entier 
        # or c'est impossible car illogique
        except ValueError:
            # Donc on découpe le string en deux au niveau de l'espace
            groupInfo = str(self.colles[line, weekColumn].value).split(" ")

            # Et on attribu le chiffre au nom de groupe et la lettre
            # au frGroup (="groupe de francais")
            frGroup = groupInfo[1]
            group = int(groupInfo[0])

        # Si le groupe de kholle n'a toujours pas été ajouté au dico
        if group not in self.khollesByGroup:
            self.khollesByGroup[group] = []

        kholleInfos = {
            "subject": subject,
            "teacher": teacher,
            "infos": infos,
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
        nextMonday = self._get_current_week() + "-" + str(datetime.today().year)
        
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
            firstDate = nextMondayTimestamp.timestamp() + days[date[0]] * nbSecondsInDay + int(date[1].split("h")[0])*nbSecondsInHour + minutes
            secondDate = nextMondayTimestamp.timestamp() + days[date[0]] * nbSecondsInDay + int(date[1].split("h")[1])*nbSecondsInHour + minutes

        else:
            # On prend le timestamp du premier lundi de la semaine, on lui
            # ajoute le nb de jours correspondant pour atteindre le jour voulu
            # et ainsi pour l'heure
            firstDate = nextMondayTimestamp.timestamp() + days[date[0]] * nbSecondsInDay + int(date[1].split("-")[0])*nbSecondsInHour 
            secondDate = nextMondayTimestamp.timestamp() + days[date[0]] * nbSecondsInDay + int(date[1].split("-")[1])*nbSecondsInHour

        # Tuple contenant le debut de l'heure et la fin de l'heure
        return (int(firstDate), int(secondDate))


    def weeklySummup(self) -> str:
        """
        Fonction qui retourne le message à afficher aux élèves

        Parameters : None
        Returns : string
        """
        # Mise à jour des informations
        self.main()
        
        # Si en mode DEBUG, on ne fait pas de mention à mp2i
        if self.debug:
            finalMessage = "wsh les prépas, c'est l'heure du collométrage de la semaine du **{}** WOUHOU\n\n".format(
                self._get_current_week()
            )
            
        else:
            finalMessage = "wsh <@&{}>, c'est l'heure du collométrage de la semaine du **{}** WOUHOU\n\n".format(
                self.classMention, self._get_current_week()
            )

        # Triage des kholles selon l'ordre croissant des groupes
        self.sort_kholles()

        # Parcours de tous les groupes déjà triés
        for group, colles in self.khollesByGroup.items():
            currentGroupMessage = "<:e:999621115406205029> **Groupe {}** : \n".format(group)

            # Création d'un message pour chaque colle du groupe actuel
            for i in range(len(colles)): 
                # Mise en forme, ajout d'un espace au debut du message
                currentGroupMessage += "> • "
                
                currentGroupMessage += "`{}` : <t:{}:f> en __{}__ avec {}".format(
                    colles[i]["subject"], self._convert_datetime_to_timestamp(colles[i]["horaries"])[0], colles[i]["class"], 
                    colles[i]["teacher"])

                # Si c'est une colle de fr, alors il y a des infos sur la lettre
                # qui passe, donc on peut l'ajouter au message
                if colles[i]["frGroup"] != None:
                    currentGroupMessage += " pour la lettre {}".format(colles[i]["frGroup"])

                currentGroupMessage += " \n"

            finalMessage += currentGroupMessage + "\n" # Saut de ligne entre les groupes

        finalMessage += "⚠️ Coquilles possibles ! *(comme Noyer avec ses transparents)*"
        return finalMessage

    def main(self) -> None:
        """
        Fonction principale du programme

        Parameters : None
        Returns : None
        """
        weekColumn = self._get_column_from_week()
        for line in range(self.firstGroupCell[0], self.lastGroupCell[0]+1):
            self._add_kholle_info_to_group(line, weekColumn)


if __name__ == "__main__":
    collometrique = Collometre(file="MPI.xls", debug=True)
    print(collometrique.weeklySummup())
