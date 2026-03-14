import json


class Data:
    """
    Classe Data
    Contient deux méthodes permettant l'ouverture d'un fichier json pour en extraire les données ou pour en écrire.
    """

    def __init__(self, file_path: str):
        """Initialisation de la classe Data
        Arguments : file_path (str) : Le chemin du fichier sur lequel on va agir.
        """

        self.file_path = file_path





    # /-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==
    # | Dans le cas où la valeur stoquée est un dictionnaire
    # \-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==

    def load_json(self) -> dict:
        """
        Ouvre un fichier json et en extrait les données sous forme de dictionnaire
        """

        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)
        

    def save_json(self, data: dict):
        """
        Ouvre un fichier json et y écrit des données entrées sous forme de dictionnaire
        """

        assert isinstance(data, dict), "Paramètres incorrectes, veuillez entrer un dictionnaire pour 'data'"

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)





    # /-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==
    # | Dans le cas où la valeur stoquée est une liste
    # \-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==

    def load_json_list(self) -> list:
        """
        Ouvre un fichier json et en extrait les données sous forme de liste
        """

        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)
        
        
    def save_json_list(self, data: list):
        """
        Ouvre un fichier json et y écrit des données entrées sous forme de liste
        """
        
        assert isinstance(data, list), "Paramètres incorrectes, veuillez entrer un liste pour 'data'"

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)