from db import Database
bot_token = "token"
host = "127.0.0.1"
db_name = "casino_telegram_bot"
user = "postgres"
password = "password"

client = Database(host=host, database=db_name, user=user, password=password)
users_list = client.get_users()
