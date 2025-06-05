import os
import mysql.connector
import boto3

def get_mysql_host():
    client = boto3.client('rds')
    return client.describe_db_instances(DBInstanceIdentifier=os.environ["MYSQL_DB_INSTANCE"])['DBInstances'][0]['Endpoint']['Address']

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

    def populate_database(self, num_posts=5, comments_per_post=3):
        self.set_connection()
        print(f"Populating database with {num_posts} posts...")
        
        # Sample post data
        posts = [
            {
                "title": "The Future of Renewable Energy",
                "content": "Solar and wind power are transforming our energy landscape with unprecedented efficiency gains. New photovoltaic materials promise 50% efficiency rates, while offshore wind farms now power entire cities. The energy transition is accelerating faster than predicted.",
                "author": "Eco Warrior",
                "category": "Renewable Energy",
                "image_url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800"
            },
            {
                "title": "Urban Farming Revolution",
                "content": "Vertical farms in city centers are reducing food miles by 90%. Using hydroponics and AI-powered climate control, these farms produce 100x more food per square foot than traditional agriculture while using 95% less water. The future of food is hyper-local.",
                "author": "Green Thumb",
                "category": "Sustainable Agriculture",
                "image_url": "https://images.unsplash.com/photo-1593118247619-e2d6f056869e?w=800"
            },
            {
                "title": "Plastic-Eating Enzymes Breakthrough",
                "content": "Scientists have engineered enzymes that can break down PET plastic in 24 hours instead of centuries. This discovery could revolutionize recycling and help clean our oceans. The enzymes work at room temperature, making the process energy-efficient.",
                "author": "BioTech Pioneer",
                "category": "Eco-Technology",
                "image_url": "https://images.unsplash.com/photo-1580870964666-b3bd73b4d0c5?w=800"
            },
            {
                "title": "Great Barrier Reef Restoration Success",
                "content": "Coral IVF techniques have shown remarkable success in restoring damaged reef sections. Baby coral survival rates have increased by 500% using new settlement methods. This gives hope for reef systems worldwide facing climate change impacts.",
                "author": "Marine Biologist",
                "category": "Conservation",
                "image_url": "https://images.unsplash.com/photo-1542691457-1c8dd6e7f8b3?w=800"
            },
            {
                "title": "Electric Aviation Takes Flight",
                "content": "The first commercial electric aircraft completed its maiden voyage carrying 30 passengers 500 miles on a single charge. With battery energy density improving 15% annually, regional electric flights will be commonplace by 2030.",
                "author": "Sky Innovator",
                "category": "Green Transportation",
                "image_url": "https://images.unsplash.com/photo-1559815442-1b8d0f8a9e4d?w=800"
            }
        ]
        
        # Sample comment data
        comments = [
            "This gives me so much hope for our planet!",
            "I'd love to see more technical details about the implementation.",
            "How can I get involved in similar projects in my community?",
            "The economic implications of this are staggering - green jobs are the future!",
            "We need government policies to accelerate adoption of these technologies.",
            "The before/after photos are incredible - nature's resilience is amazing.",
            "What's the scalability of this solution? Can it work globally?",
            "I've been following this research for years - thrilled to see it working!",
            "How does this compare to traditional methods in terms of cost efficiency?",
            "This could revolutionize developing nations' energy infrastructure."
        ]
        
        post_ids = []
        for i, post in enumerate(posts[:num_posts]):
            post_id = self.create_post(**post)
            post_ids.append(post_id)
            
            for j in range(comments_per_post):
                comment_index = (i * comments_per_post + j) % len(comments)
                self.create_comment(
                    post_id=post_id,
                    name=f"Commenter {j+1}",
                    comment=comments[comment_index]
                )
        
        print("Database population complete!")
        return post_ids