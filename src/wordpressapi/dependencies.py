from woocommerce import API
import os
from dotenv import load_dotenv

load_dotenv()

wcapi = API(
    url = os.getenv("WOOCOMMERCE_URL"),
    consumer_key = os.getenv("WOOCOMMERCE_CONSUMER_KEY"),
    consumer_secret = os.getenv("WOOCOMMERCE_SECRET_KEY"),
    version="wc/v3",
    timeout=20
)

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_API_KEY = os.getenv("ODOO_API_KEY")