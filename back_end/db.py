import os
import json
import mysql.connector
import boto3

def get_mysql_host():
    client = boto3.client('rds')
    instances = client.describe_db_instances(DBInstanceIdentifier=os.environ["MYSQL_DB_INSTANCE"])
    return instances['DBInstances'][0]['Endpoint']['Address']

class DBHandler:
    __connection = None

    def set_connection(self):
        if not self.__connection:
            self.__connection = mysql.connector.connect(
                host=get_mysql_host(),
                database=os.environ["MYSQL_DATABASE"],
                user=os.environ["MYSQL_USER"],
                password=os.environ["MYSQL_PASSWORD"]
            )
            self.__create_tables()

    def __create_tables(self):
        cursor = self.__connection.cursor()
        # Create posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                author VARCHAR(100),
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                category VARCHAR(50),
                image_url VARCHAR(255)
            )
        """)
        
        # Create comments table with post_id foreign key
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INT PRIMARY KEY AUTO_INCREMENT,
                post_id INT NOT NULL,
                name VARCHAR(100),
                comment TEXT NOT NULL,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
            )
        """)
        self.__connection.commit()

    # Post methods
    def create_post(self, title, content, author, category, image_url):
        self.set_connection()
        cursor = self.__connection.cursor()
        cursor.execute(
            "INSERT INTO posts (title, content, author, category, image_url) VALUES (%s, %s, %s, %s, %s)",
            (title, content, author, category, image_url)
        )
        self.__connection.commit()
        return cursor.lastrowid

    def get_posts(self, limit=10, offset=0):
        self.set_connection()
        cursor = self.__connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM posts ORDER BY date DESC LIMIT %s OFFSET %s", (limit, offset))
        return cursor.fetchall()

    def get_post(self, post_id):
        self.set_connection()
        cursor = self.__connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
        return cursor.fetchone()

    # Comment methods
    def create_comment(self, post_id, name, comment):
        self.set_connection()
        cursor = self.__connection.cursor()
        cursor.execute(
            "INSERT INTO comments (post_id, name, comment) VALUES (%s, %s, %s)",
            (post_id, name, comment)
        )
        self.__connection.commit()

    def get_comments(self, post_id):
        self.set_connection()
        cursor = self.__connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM comments WHERE post_id = %s ORDER BY date ASC", (post_id,))
        return cursor.fetchall()

    def get_comment_count(self, post_id):
        self.set_connection()
        cursor = self.__connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM comments WHERE post_id = %s", (post_id,))
        return cursor.fetchone()[0]
