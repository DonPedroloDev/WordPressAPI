from woocommerce import API

# Configuración de la conexión
wcapi = API(
    url="http://localhost:8080", # Asegúrate de que el puerto sea el correcto (8080)
    consumer_key="ck_f6731ec8696f0c00fdb54c5b929f3bf671ea1f16",
    consumer_secret="cs_50f271c2a00faaf9d37787d54a5713ea18a0faca",
    version="wc/v3",
    timeout=20
)