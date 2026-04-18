from woocommerce import API

# Configuración de la conexión
wcapi = API(
    url="http://localhost:8080", # Asegúrate de que el puerto sea el correcto (8080)
    consumer_key="ck_b94f8db11dba9585630408e11415e45a7fd843f9",
    consumer_secret="cs_2d5c790adfaf1160a7ea7633101f5360ffbee6b5",
    version="wc/v3",
    timeout=20
)