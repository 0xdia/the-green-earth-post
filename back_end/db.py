import os
import json
import mysql.connector
import boto3

def get_mysql_host():
    client = boto3.client('rds')
    instances = client.describe_db_instances(
        DBInstanceIdentifier=os.environ["MYSQL_DB_INSTANCE"]
    )
    return instances['DBInstances'][0]['Endpoint']['Address']

class CommentDB:
    __connection = None

    def set_connection(self):
        if not self.__connection:
            self.__connection = mysql.connector.connect(
                host=get_mysql_host(),
                database=os.environ["MYSQL_DATABASE"],
                user=os.environ["MYSQL_USER"],
                password=os.environ["MYSQL_PASSWORD"]
            )
            self.__create_table()

    def __create_table(self):
        cursor = self.__connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                name VARCHAR(100),
                comment VARCHAR(255),
                date VARCHAR(100)
            )
        """)

    def get_comments(self):
        self.set_connection()
        cursor = self.__connection.cursor()
        cursor.execute("""
            SELECT JSON_ARRAYAGG(JSON_OBJECT(
                'name', name, 
                'comment', comment, 
                'date', date
            )) FROM comments
        """)
        result = cursor.fetchone()[0]
        return json.loads(result) if result else []

    def insert_comment(self, name, comment, date):
        self.set_connection()
        cursor = self.__connection.cursor()
        cursor.execute(
            f"INSERT INTO comments (name, comment, date) VALUES ('{name}', '{comment}', '{date}')"
        )
        self.__connection.commit()
