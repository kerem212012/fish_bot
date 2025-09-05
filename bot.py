import telebot
from environs import Env


env = Env()
env.read_env()
bot = telebot.TeleBot(env.str("TG_TOKEN"))

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.send_message(message.chat.id, "Привет!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.send_message(message.chat.id, message.text)

bot.infinity_polling()