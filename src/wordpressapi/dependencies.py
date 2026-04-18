from woocommerce import API

# Configuración de la conexión
wcapi = API(
    url="http://localhost:8080", # Asegúrate de que el puerto sea el correcto (8080)
    consumer_key="ck_X",
    consumer_secret="cs_X",
    version="wc/v3",
    timeout=20
)