from psycopg2 import connect


class Database:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = connect(
            host=self.host, user=self.user, password=self.password, database=self.database)
        self.cursor = self.connection.cursor()

    def create_user(self, user_id, username):
        self.cursor.execute(f"""
                        insert into user_data values('{user_id}', '{username}', 500, 0)
                            """)
        self.connection.commit()

    def get_users(self):
        self.cursor.execute("""select id from user_data;""")
        info = self.cursor.fetchall()
        users_list = [b[0] for b in info]
        return users_list

    def get_balance(self, user_id):
        self.cursor.execute(f"""select balance from user_data where id = '{user_id}';""")
        info = self.cursor.fetchall()
        return info[0][0]

    def get_games_played(self, user_id):
        self.cursor.execute(f"""select games_played from user_data where id = '{user_id}';""")
        info = self.cursor.fetchall()
        return info[0][0]

    def get_best_players(self, by_activity=False):
        if by_activity:
            self.cursor.execute("""
                                select username, balance, games_played 
                                from user_data 
                                order by games_played desc
                                limit 10;
                                """)

        else:
            self.cursor.execute("""
                                select username, balance, games_played 
                                from user_data 
                                order by balance desc
                                limit 10;
                                """)
        return self.cursor.fetchall()

    def set_balance(self, user_id, balance):
        self.cursor.execute(f"""
                                update user_data
                                set balance = {balance}
                                where id = '{user_id}';
                                """)
        self.connection.commit()

    def set_games_played(self, user_id, games_played):
        self.cursor.execute(f"""
                                update user_data
                                set games_played = {games_played}
                                where id = '{user_id}';
                                """)
        self.connection.commit()

    def update(self, user_id, balance, games_played):
        self.cursor.execute(f"""
                        update user_data
                        set balance = {balance}, games_played = {games_played}
                        where id = '{user_id}';
                        """)
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
