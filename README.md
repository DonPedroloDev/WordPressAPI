# WordPressAPI

## API minima

El proyecto quedo limpio y centrado solo en sincronizar productos de Odoo hacia WooCommerce.

Router principal:

- [src/wordpressapi/src/routers/odoo_woocommerce_router.py](src/wordpressapi/src/routers/odoo_woocommerce_router.py)

Endpoint disponible:

- `GET /SincronizarOddoConWooCommerce/`

La configuracion esta hardcodeada en el router (Odoo y WooCommerce).

## Ejecutar

1. Instalar dependencias:
	- `pip install fastapi woocommerce uvicorn`
2. Iniciar API:
	- `python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload`
3. Probar docs:
	- `http://127.0.0.1:8000/docs`
