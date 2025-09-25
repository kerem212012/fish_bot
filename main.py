import requests
from environs import Env


env = Env()
env.read_env()

def create_user():
    payload = {
            "username":"bbbbbbbbbbbbb","email": "bbbbbbbbbb@gmail.com",
            "password":"bbbbbbbbbbbbbb",
    }
    headers = {
        "Authorization": f"Bearer {env.str("STRAPI_TOKEN")}"
    }
    url = "http://localhost:1337/api/auth/local/register"
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
def create_cart():
    payload = {
        "data": {
            "users_permissions_users":
                {"connect": "iau7aeyuchav2gx1btalx1tj"},
            "tg_id":"1234"
        }
    }
    headers = {
        "Authorization": f"Bearer {env.str("STRAPI_TOKEN")}"
    }
    url = "http://localhost:1337/api/carts"
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

def add_to_cart():
    payload = {
        "data": {"products": {"connect":["rgi1vv1t2pi8kvgbvm92tvuo","f9r0u6zvy2jafdx2t39fn9bt"]},"cart":{"connect":"raqkqmxuzxudaztzen48g2bv"}}
    }
    headers = {
        "Authorization": f"Bearer {env.str("STRAPI_TOKEN")}"
    }
    url = "http://localhost:1337/api/cart-items"
    response = requests.post(url, headers=headers,json=payload)
    response.raise_for_status()

def delete_item_from_cart(cart_id,product_id):
    headers = {
        "Authorization": f"Bearer {env.str("STRAPI_TOKEN")}"
    }
    url = f"http://localhost:1337/api/cart-items/{get_cart_item_id_from_product(cart_id,product_id)}"
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
product_id="rgi1vv1t2pi8kvgbvm92tvuo"
cart_id = "ywfp0mneh22ylqfimv4mrcoi"
def get_cart_item_id_from_product(cart_id,product_id):
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
delete_item_from_cart(cart_id=cart_id,product_id=product_id)
