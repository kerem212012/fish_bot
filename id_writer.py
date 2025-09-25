import requests
from environs import Env


env = Env()
env.read_env()

documentIds = ["mm2f0x6u3l0qp6ffi3wn951k","hya175fytg2ktag27jw0lode"]
headers={
        "Authorization": f"Bearer {env.str("STRAPI_TOKEN")}"
    }
url = "http://localhost:1337/api/users?populate=*"
response = requests.get(url,headers=headers)
response.raise_for_status()
data = response.json()
print(data)

