from psycopg2 import connect


class Database:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        try:
            self.connection = connect(
                host=self.host, user=self.user, password=self.password, database=self.database)
            self.cursor = self.connection.cursor()
        except Exception as ex:
            print(f"ERROR: {ex}")

    def create_user(self, user_id):
        self.cursor.execute(f"""
                        insert into user_data values({user_id}, 500, 0)
                            """)
        self.connection.commit()

    def get_users(self):
        self.cursor.execute("""select id from user_data;""")
        info = self.cursor.fetchall()
        users_list = [b[0] for b in info]
        return users_list

    def get_info(self, user_id):
        self.cursor.execute(f"""select balance, games_played from user_data where id = {user_id};""")
        info = self.cursor.fetchall()
        data = list(info[0])
        return data

    def update(self, user_id, balance, games_played):
        self.cursor.execute(f"""
                        update user_data
                        set balance = {balance}, games_played = {games_played}
                        where id = {user_id};
                        """)
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
