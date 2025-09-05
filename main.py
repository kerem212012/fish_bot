import requests
from environs import Env


env = Env()
env.read_env()
headers={
    "Authorization": f"Bearer {env.str("STRAPI_TOKEN")}"
}
url = "http://localhost:1337/api/products"
response = requests.get(url,headers=headers)
response.raise_for_status()
print(response.json())