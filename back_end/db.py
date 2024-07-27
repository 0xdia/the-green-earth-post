import os
import json
import mysql.connector
import boto3


def get_mysql_host():
    """
    get_mysql_host retourne url de la base de données MySQL.
    :return: l'url de la base de données MySQL
    """

    # La variable d'environnement MYSQL_LOCAL_HOST est utilisee pour les développement en local avec Docker
    if os.environ.get("MYSQL_LOCAL_HOST"):
        return os.environ["MYSQL_LOCAL_HOST"]

    # On recupere l'url de la base de données RDS afin de s'y connecter pour lire et inserer des commentaires
    client = boto3.client('rds')
    instances = client.describe_db_instances(DBInstanceIdentifier=os.environ["MYSQL_DB_INSTANCE"])
    return instances.get('DBInstances')[0].get('Endpoint').get('Address')


class CommentDB:
    __connection = None

    def set_connection(self):
        """
        set_connection établit une connexion avec la base de données RDS
        et initialise la variable local __connection
        et crée la table Comments avec la fonction __create_table
        """
        if not self.__connection:
            self.__connection = mysql.connector.connect(host=get_mysql_host(),
                                                        database=os.environ["MYSQL_DATABASE"],
                                                        user=os.environ["MYSQL_USER"],
                                                        password=os.environ["MYSQL_PASSWORD"])
            self.__create_table()

    def __create_table(self):
        """
        __create_table crée la table Comments si elle n existe pas deja
        """
        try:
            cursor = self.__connection.cursor()
            cursor.execute("""
                CREATE TABLE comments
                (
                    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                    name VARCHAR(100),
                    comment VARCHAR(255),
                    date VARCHAR(100)
                );
            """)
            cursor.fetchone()
            print("Table created")
        except Exception as ex:
            print(ex)

    def __drop_table(self):
        """
        __drop_table supprime la table Comments
        """
        cursor = self.__connection.cursor()
        cursor.execute("DROP TABLE comments;")
        record = cursor.fetchone()
        return record

    def get_comments(self):
        """
        get_comments retourne les commentaires contenus dans la base de données MySQL

        :return: retourne l'ensemble des commentaires
        """
        self.set_connection()
        cursor = self.__connection.cursor()
        cursor.execute("""
            SELECT JSON_ARRAYAGG(JSON_OBJECT('name', name, 'comment', comment, 'date', date))
            FROM comments;
        """)
        record = cursor.fetchone()  
        result = record[0]
        if result:
            return json.loads(result)
        else:
            return []

    def insert_comment(self, name, comment, date):
        """
        insert_comment insère un commentaire dans la table Comments

        :param name: le nom du visiteur qui laisse un commentaire
        :param comment: le contenu du commentaire
        :param date: la date de la création du commentaire
        """
        self.set_connection()
        cursor = self.__connection.cursor()
        cursor.execute(
            f"INSERT INTO comments (name, comment, date) VALUES ('{name}', '{comment}', '{date}')"
        )
        self.__connection.commit()
