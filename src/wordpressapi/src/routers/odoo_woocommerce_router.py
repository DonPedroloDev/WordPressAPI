import xmlrpc.client
from typing import Any, cast

from fastapi import APIRouter
from woocommerce import API

router = APIRouter()

# Odoo (completa estos datos con tu instancia real)
ODOO_URL = "http://localhost:8069"
ODOO_DB = "Test1"
ODOO_USER = "qw@gm.com"
ODOO_API_KEY = "bcead35994119a6ed2869e9644749f11452b5b4d"

# WooCommerce
wcapi = API(
    url="http://localhost:8080",
    consumer_key="ck_fa2863c2634c9be27ad5efc54af4bd6655d413b3",
    consumer_secret="cs_e0364e080f98589b886b2ab38be87bd4c9726f1c",
    version="wc/v3",
    timeout=30,
)


def _get_odoo_products() -> list[dict[str, Any]]:
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_API_KEY, {})
        if not uid:
            raise ValueError(
                "No se pudo autenticar en Odoo. Revisa ODOO_USER y ODOO_API_KEY."
            )

        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        products = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_API_KEY,
            "product.template",
            "search_read",
            [[["sale_ok", "=", True]]],
            {"fields": ["id", "name", "list_price", "description_sale", "default_code"]},
        )
        return cast(list[dict[str, Any]], products)
    except xmlrpc.client.Fault as fault:
        fault_message = str(fault)
        if "does not exist" in fault_message and "database" in fault_message:
            raise ValueError(
                f"La base de datos de Odoo '{ODOO_DB}' no existe. Cambia ODOO_DB por el nombre real."
            )
        raise ValueError(f"Error XML-RPC de Odoo: {fault_message}")


def _sync_one_product(product: dict[str, Any]) -> dict[str, Any]:
    sku = product.get("default_code") or f"ODOO-{product['id']}"

    response_check = wcapi.get("products", params={"sku": sku})
    if response_check.status_code != 200:
        return {
            "status": "error",
            "error": {
                "product": product.get("name", "(sin nombre)"),
                "sku": sku,
                "step": "check",
                "status_code": response_check.status_code,
                "message": response_check.text,
            },
        }

    product_data = {
        "name": product.get("name") or f"Producto Odoo {product['id']}",
        "type": "simple",
        "regular_price": str(product.get("list_price", 0)),
        "description": product.get("description_sale") or "",
        "sku": sku,
    }

    existing = response_check.json()
    if existing:
        product_id = existing[0]["id"]
        response = wcapi.put(f"products/{product_id}", product_data)
        if response.status_code in (200, 201):
            return {"status": "updated"}

        return {
            "status": "error",
            "error": {
                "product": product_data["name"],
                "sku": sku,
                "step": "update",
                "status_code": response.status_code,
                "message": response.text,
            },
        }

    response = wcapi.post("products", product_data)
    if response.status_code in (200, 201):
        return {"status": "created"}

    return {
        "status": "error",
        "error": {
            "product": product_data["name"],
            "sku": sku,
            "step": "create",
            "status_code": response.status_code,
            "message": response.text,
        },
    }


@router.get("/SincronizarOddoConWooCommerce/")
def sincronizar_odoo_con_woocommerce():
    try:
        products = _get_odoo_products()
        created = 0
        updated = 0
        errors = []

        for product in products:
            result = _sync_one_product(product)
            if result["status"] == "created":
                created += 1
            elif result["status"] == "updated":
                updated += 1
            else:
                errors.append(result["error"])

        return {
            "ok": True,
            "total_odoo": len(products),
            "creados": created,
            "actualizados": updated,
            "errores": errors,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
