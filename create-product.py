import os
from woocommerce import API
#from dotenv import load_dotenv

# Cargar variables del archivo .env
#load_dotenv()

wcapi = API(
    url="http://localhost:8080",
    consumer_key="",
    consumer_secret="",
    version="wc/v3"
)

# Ejemplo: Crear un producto simple
data = {
    "name": "Producto de Prueba API",
    "type": "simple",
    "regular_price": "150.00",
    "description": "Creado desde Python en localhost",
    "categories": [{"id": 1}] # Asegúrate de que el ID de categoría existe
}

print(wcapi.post("products", data).json())
