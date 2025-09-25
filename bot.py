import requests
import telebot
from environs import Env
from telebot import types

env = Env()
env.read_env()
bot = telebot.TeleBot(env.str("TG_TOKEN"))
strapi_token = env.str("STRAPI_TOKEN")


def create_user(username, tg_id):
    payload = {
        "username": username, "email": f"{tg_id}@gmail.com",
        "password": str(tg_id),"tg_id":str(tg_id)
    }
    headers = {
        "Authorization": f"Bearer {strapi_token}"
    }
    url = "http://localhost:1337/api/auth/local/register"
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()


def get_data(id=None):
    params = {
        "populate": "*"
    }
    headers = {
        "Authorization": f"Bearer {strapi_token}"
    }
    if id:
        url = f"http://localhost:1337/api/products/{id}"
    else:
        url = "http://localhost:1337/api/products"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def create_cart(tg_id):
    payload = {
        "data": {
            "users_permissions_users": {"connect": get_user_document_id(tg_id)},
            "tg_id": str(tg_id)
        }
    }
    headers = {
        "Authorization": f"Bearer {strapi_token}"
    }
    url = "http://localhost:1337/api/carts"
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()


def add_to_cart(tg_id, product_id):
    payload = {
        "data": {"products": {"connect": product_id}, "cart": {"connect": get_cart_document_id(tg_id)}}
    }
    headers = {
        "Authorization": f"Bearer {strapi_token}"
    }
    url = "http://localhost:1337/api/cart-items"
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()


def get_user_document_id(tg_id):
    headers = {
        "Authorization": f"Bearer {env.str("STRAPI_TOKEN")}"
    }
    url = "http://localhost:1337/api/users?populate=*"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    users = response.json()
    for user in users:
        if user["tg_id"] == str(tg_id):
            return user["documentId"]


def get_cart_document_id(tg_id):
    headers = {
        "Authorization": f"Bearer {strapi_token}"
    }
    url = "http://localhost:1337/api/carts?populate=*"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    carts = response.json()
    for cart in carts["data"]:
        if cart["tg_id"] == str(tg_id):
            return cart["documentId"]


def get_cart_items_id(tg_id):
    headers = {
        "Authorization": f"Bearer {strapi_token}"
    }
    url = "http://localhost:1337/api/carts?populate=*"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    ids = []
    for object in data["data"]:
        if object["tg_id"] == str(tg_id):
            for item in object["cart_items"]:
                ids.append(item["documentId"])
    return ids


def get_product_id_from_cart_item(cart_item_ids):
    headers = {
        "Authorization": f"Bearer {strapi_token}"
    }
    url = "http://localhost:1337/api/cart-items?populate=*"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    ids = []
    for object in data["data"]:
        if object["documentId"] in cart_item_ids:
            for product in object["products"]:
                ids.append(product["documentId"])
    return ids


def delete_item_from_cart(cart_id, product_id):
    headers = {
        "Authorization": f"Bearer {env.str("STRAPI_TOKEN")}"
    }
    url = f"http://localhost:1337/api/cart-items/{get_cart_item_id_from_product(cart_id, product_id)}"
    response = requests.delete(url, headers=headers)
    response.raise_for_status()


product_id = "rgi1vv1t2pi8kvgbvm92tvuo"
cart_id = "ywfp0mneh22ylqfimv4mrcoi"


def get_cart_item_id_from_product(cart_id, product_id):
    headers = {
        "Authorization": f"Bearer {env.str("STRAPI_TOKEN")}"
    }
    url = "http://localhost:1337/api/cart-items?populate=*"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    for object in data["data"]:
        if object["cart"]["documentId"] == cart_id and object["products"][0]["documentId"] == product_id:
            return object["documentId"]


@bot.message_handler(commands=['start'])
def start(message):
    create_user(username=message.chat.first_name, tg_id=message.chat.id)
    create_cart(tg_id=message.chat.id)
    markup = types.InlineKeyboardMarkup()
    menu_btn = types.InlineKeyboardButton("Меню", callback_data="back")
    cart_btn = types.InlineKeyboardButton("Моя корзина", callback_data="cart")
    markup.row(menu_btn)
    markup.row(cart_btn)
    bot.send_message(message.chat.id, "Please choose:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = get_data()["data"]
    ids = []
    for object in data:
        ids.append(object["documentId"])
    if call.data == "cart":
        markup = types.InlineKeyboardMarkup()
        product_ids = get_product_id_from_cart_item(get_cart_items_id(call.message.chat.id))
        for product_id in product_ids:
            data = get_data(product_id)
            btn = types.InlineKeyboardButton(f"Отказ {data["data"]["title"]}",
                                             callback_data=f"delete_item|{product_id}")
            markup.row(btn)
            bot.send_message(call.message.chat.id, text=data["data"]["title"])
        menu_btn = types.InlineKeyboardButton("В Меню", callback_data="back")
        markup.row(menu_btn)
        bot.send_message(call.message.chat.id, text="Вы можете удалить товары:", reply_markup=markup)
    if call.data.split("|", 1)[0] == "delete_item":
        delete_item_from_cart(cart_id=get_cart_document_id(call.message.chat.id), product_id=call.data.split("|", 1)[1])
        bot.send_message(call.message.chat.id, text="Отмена Товара успешна")
    if call.data in ids:
        markup = types.InlineKeyboardMarkup()
        data = get_data(call.data)
        photo_url = f"http://localhost:1337{data["data"]["picture"]["url"]}"
        response = requests.get(photo_url)
        response.raise_for_status()
        back_btn = types.InlineKeyboardButton("Назад", callback_data="back")
        add_to_cart_btn = types.InlineKeyboardButton("Добавить в корзину", callback_data=f"add_to_cart|{call.data}")
        markup.row(add_to_cart_btn)
        markup.row(back_btn)
        bot.send_photo(call.message.chat.id, photo=response.content, caption=data["data"]["description"],
                       reply_markup=markup)
    if call.data == "back":
        markup = types.InlineKeyboardMarkup()
        data = get_data()["data"]
        for object in data:
            btn = types.InlineKeyboardButton(object["title"], callback_data=object["documentId"])
            markup.row(btn)
        bot.send_message(call.message.chat.id, "Меню:", reply_markup=markup)
    if call.data.split("|", 1)[0] == "add_to_cart":
        add_to_cart(tg_id=call.message.chat.id, product_id=call.data.split("|", 1)[1])


bot.infinity_polling()
