from random import choice
from time import sleep
from math import floor
from telebot import TeleBot, types
import config1 as config
from db import Database

db_client = Database(
    host=config.db_host,
    database=config.db_name,
    user=config.db_user,
    password=config.db_password
)


class Player:
    def __init__(self, user_id, username):
        self.username = username
        self.user_id = user_id
        self._balance = 500
        self._games_played = 0

    def get_info(self):
        self._balance = db_client.get_balance(self.user_id)
        self._games_played = db_client.get_games_played(self.user_id)

    def create_user(self):
        db_client.create_user(self.user_id, self.username)

    def __get_balance(self):
        return self._balance

    def __set_balance(self, value):
        self._balance = value
        db_client.set_balance(self.user_id, value)

    def __del_balance(self):
        del self._balance

    def __get_games_played(self):
        return self._games_played

    def __set_games_played(self, value):
        self._games_played = value
        db_client.set_games_played(self.user_id, value)

    def __del_games_played(self):
        del self._games_played

    balance = property(
        fget=__get_balance,
        fset=__set_balance,
        fdel=__del_balance
    )

    games_played = property(
        fget=__get_games_played,
        fset=__set_games_played,
        fdel=__del_games_played
    )


class Bot:
    action_markup = types.ReplyKeyboardMarkup()
    action_markup.add("Play")
    action_markup.add("Show statistics")
    action_markup.add("Show best players")

    def __init__(self, bot_token):
        self.bot = TeleBot(bot_token, skip_pending=True)
        self.player = None
        self.start = self.bot.message_handler(commands=['start'])(self.start)
        self.bot.polling(none_stop=True)

    def start(self, message):
        if str(message.from_user.id) in db_client.get_users():
            username = message.from_user.first_name
            if message.from_user.last_name is not None:
                username += f" {message.from_user.last_name}"
            self.player = Player(str(message.from_user.id), username)
            self.player.get_info()
            self.bot.register_next_step_handler(
                self.bot.send_message(message.from_user.id, "Select action", reply_markup=self.action_markup),
                self.select_action
            )
        else:
            self.bot.send_message(message.from_user.id, "Welcome to our casino! We give you 500 free coins, enjoy!")
            username = message.from_user.first_name
            if message.from_user.last_name is not None:
                username += f" {message.from_user.last_name}"
            self.player = Player(str(message.from_user.id), username)
            self.player.create_user()
            self.bot.register_next_step_handler(
                self.bot.send_message(message.from_user.id, "Select action", reply_markup=self.action_markup),
                self.select_action
            )

    def select_action(self, message):
        if message.text == "Play":
            markup = types.ReplyKeyboardMarkup()
            markup.add(str(self.player.balance))
            markup.add(str(floor(self.player.balance / 2)))
            markup.add(str(floor(self.player.balance / 4)))
            self.bot.register_next_step_handler(
                self.bot.send_message(message.from_user.id, "Place your bet", reply_markup=markup), self.play
            )
        elif message.text == "Show statistics":
            self.bot.send_message(
                message.from_user.id,
                f"Your balance is {self.player.balance}\nYou played {self.player.games_played} games"
            )
            self.bot.register_next_step_handler(
                self.bot.send_message(message.from_user.id, "Select action", reply_markup=self.action_markup),
                self.select_action,
            )
        elif message.text == "Show best players":
            markup = types.ReplyKeyboardMarkup()
            markup.add("by balance")
            markup.add("by activity")
            self.bot.register_next_step_handler(
                self.bot.send_message(message.from_user.id, "Order by: ", reply_markup=markup),
                self.show_best_players,
            )

        else:
            self.bot.register_next_step_handler(
                self.bot.send_message(message.from_user.id, "Select action", reply_markup=self.action_markup),
                self.select_action,
            )

    def show_best_players(self, message):
        mode = message.text
        output = ""
        if mode == "by balance":
            info = db_client.get_best_players()
            self.bot.send_message(message.from_user.id, "The richest players")
            for best_player in info:
                output += f"{best_player[0]}\nBalance: {best_player[1]}\nGames played: {best_player[2]}\n"
            self.bot.send_message(message.from_user.id, output)
        elif mode == "by activity":
            self.bot.send_message(message.from_user.id, "The most active players")
            info = db_client.get_best_players(by_activity=True)
            for best_player in info:
                output += f"{best_player[0]}\nBalance: {best_player[1]}\nGames played: {best_player[2]}\n"
            self.bot.send_message(message.from_user.id, output)
        else:
            self.bot.register_next_step_handler(
                self.bot.send_message(message.from_user.id, "Order by: "), self.show_best_players
            )
        self.bot.register_next_step_handler(
            self.bot.send_message(message.from_user.id, "Select action", reply_markup=self.action_markup),
            self.select_action
        )

    def play(self, message):
        self.player.get_info()
        bet_placed = False
        try:
            bet = int(message.text)
            bet_placed = True
        except ValueError:
            self.bot.register_next_step_handler(
                self.bot.send_message(message.from_user.id, "Place your bet"), self.play
            )
        if bet_placed:
            if bet > self.player.balance or bet < 1:
                self.bot.send_message(message.from_user.id, "Your balance is too low")
                self.bot.register_next_step_handler(
                    self.bot.send_message(message.from_user.id, "Place your bet"), self.play
                )
            else:
                self.player.balance -= bet
                self.player.games_played += 1
                win = choice((True, False))
                output = "Lose"
                msg = self.bot.send_message(message.from_user.id, "Win")
                for q in range(5):
                    sleep(0.5)
                    self.bot.edit_message_text("Lose", message.from_user.id, msg.message_id)
                    sleep(0.5)
                    self.bot.edit_message_text("Win", message.from_user.id, msg.message_id)
                if win:
                    self.player.balance += bet * 2
                    output = "Win"
                self.bot.edit_message_text(f"{output}\nYour balance is {self.player.balance}", message.from_user.id, msg.message_id)
                if self.player.balance <= 0:
                    self.bot.send_message(message.from_user.id, "Seems like you don't have coins. Take this 10 coins.")
                    self.player.balance = 10
                self.bot.register_next_step_handler(
                    self.bot.send_message(message.from_user.id, "Select action", reply_markup=self.action_markup),
                    self.select_action,
                )

if __name__ == "__main__":
    Bot(config.bot_token)
