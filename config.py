from db import Database
bot_token = "5636814074:AAETlsUroMjtMkQinVDKtPMYzlBaTrQ85Pk"
host = "127.0.0.1"
db_name = "casino_telegram_bot"
user = "postgres"
password = "postpass"

client = Database(host=host, database=db_name, user=user, password=password)
users_list = client.get_users()
