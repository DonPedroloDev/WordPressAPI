from woocommerce import API

# Configuración de la conexión
wcapi = API(
    url="http://localhost:8080", # Asegúrate de que el puerto sea el correcto (8080)
    consumer_key="ck_f6731ec8696f0c00fdb54c5b929f3bf671ea1f16",
    consumer_secret="cs_50f271c2a00faaf9d37787d54a5713ea18a0faca",
    version="wc/v3",
    timeout=20
)

# Obtener la lista de productos (limitado a los últimos 10)
try:
    response = wcapi.get("products", params={"per_page": 10})
    
    # Verificar si la respuesta fue exitosa
    if response.status_code == 200:
        productos = response.json()
        print(f"--- Se encontraron {len(productos)} productos ---")
        
        for p in productos:
            #print(p)	
            print(f"ID: {p['id']} | Nombre: {p['name']} | Precio: ${p['price']}")
    else:
        print(f"Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"Hubo un error de conexión: {e}")
