from random import choice
from time import sleep
from telebot import TeleBot, types
from config import *


class Player:
    def __init__(self, user_id):
        self.user_id = user_id
        self.balance = 500
        self.games_played = 0

    def get_info(self):
        info = client.get_info(self.user_id)
        self.balance = info[0]
        self.games_played = info[1]

    def update(self):
        client.update(self.user_id, self.balance, self.games_played)

    def create_user(self):
        client.create_user(self.user_id)


bot = TeleBot(bot_token)


@bot.message_handler(content_types=["text"])
def start(message):
    if message.from_user.id in users_list:
        markup = types.ReplyKeyboardMarkup()
        markup.add("Play")
        markup.add("Show statistics")
        player = Player(message.from_user.id)
        player.get_info()
        bot.register_next_step_handler(
            bot.send_message(message.from_user.id, "Select action", reply_markup=markup), select_action, player
        )
    else:
        bot.send_message(message.from_user.id, "Welcome to our casino! We give you 500 free coins, enjoy!")
        player = Player(message.from_user.id)
        player.create_user()
        markup = types.ReplyKeyboardMarkup()
        markup.add("Play")
        markup.add("Show statistics")
        bot.register_next_step_handler(
            bot.send_message(message.from_user.id, "Select action", reply_markup=markup), select_action, player
        )


def select_action(message, player):
    markup = types.ReplyKeyboardMarkup()
    markup.add("Play")
    markup.add("Show statistics")
    if message.text == "Play":
        bot.register_next_step_handler(
            bot.send_message(message.from_user.id, "Place your bet"), play, player
        )
    elif message.text == "Show statistics":
        bot.send_message(
            message.from_user.id, f"Your balance is {player.balance}\nYou played {player.games_played} games")
        bot.register_next_step_handler(
            bot.send_message(message.from_user.id, "Select action", reply_markup=markup), select_action, player
        )
    else:
        bot.register_next_step_handler(
            bot.send_message(message.from_user.id, "Select action", reply_markup=markup), select_action, player
        )


def play(message, player):
    player.get_info()
    try:
        markup = types.ReplyKeyboardMarkup()
        markup.add("Play")
        markup.add("Show statistics")
        bet = int(message.text)
        if bet > player.balance or bet < 1:
            bot.send_message(message.from_user.id, "Your balance is too low")
            bot.register_next_step_handler(
                bot.send_message(message.from_user.id, "Place your bet"), play, player
            )
        else:
            player.balance -= bet
            player.games_played += 1
            win = choice((True, False))
            for q in range(5):
                msg = bot.send_message(message.from_user.id, "Win")
                sleep(0.5)
                bot.delete_message(message.from_user.id, msg.message_id)
                msg = bot.send_message(message.from_user.id, "Lose")
                sleep(0.5)
                bot.delete_message(message.from_user.id, msg.message_id)
            if win:
                player.balance += bet * 2
                bot.send_message(message.from_user.id, f"Win\nYour balance is {player.balance}")
            else:
                bot.send_message(message.from_user.id, f"Lose\nYour balance is {player.balance}")
            player.update()
            if player.balance <= 0:
                bot.send_message(message.from_user.id, "Seems like you don't have coins. Take this 10 coins.")
                player.balance = 10
                player.update()
            bot.register_next_step_handler(
                bot.send_message(message.from_user.id, "Select action", reply_markup=markup), select_action, player
            )
    except ValueError:
        bot.register_next_step_handler(
            bot.send_message(message.from_user.id, "Place your bet"), play, player
        )


try:
    bot.polling(none_stop=True)
except Exception as ex:
    print(ex)
finally:
    client.close()
