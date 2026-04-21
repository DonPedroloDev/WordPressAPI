from fastapi import APIRouter, HTTPException
from ...dependencies import wcapi, ODOO_API_KEY, ODOO_DB, ODOO_URL, ODOO_USER
import xmlrpc.client
import json
import os

router = APIRouter()

PROCESSED_FILE = "processed_orders.json"


# -------------------------
# Persistencia local
# -------------------------
def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return set()

    try:
        with open(PROCESSED_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_processed(data):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(data), f)


# -------------------------
# Odoo connection
# -------------------------
def connect_odoo():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_API_KEY, {})

    if not uid:
        raise Exception("Error autenticando en Odoo")

    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    return uid, models


def get_odoo_orders(models, uid):
    return models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_API_KEY,
        'sale.order',
        'search_read',
        [[]],
        {
            'fields': ['id', 'name', 'partner_id', 'amount_total', 'order_line'],
            'limit': 10
        }
    )


def get_order_lines(line_ids, models, uid):
    return models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_API_KEY,
        'sale.order.line',
        'read',
        [line_ids],
        {'fields': ['product_id', 'product_uom_qty']}
    )


def get_product_sku(product_id, models, uid):
    product = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_API_KEY,
        'product.product',
        'read',
        [[product_id]],
        {'fields': ['default_code']}
    )
    return product[0].get("default_code")


def get_wc_product_id_by_sku(sku):
    response = wcapi.get("products", params={"sku": sku})

    if response.status_code == 200 and response.json():
        return response.json()[0]["id"]

    return None



def transform_odoo_to_wc(order, models, uid):
    line_items = []

    lines = get_order_lines(order["order_line"], models, uid)

    for line in lines:
        product_id = line["product_id"][0]

        sku = get_product_sku(product_id, models, uid)
        if not sku:
            continue

        wc_product_id = get_wc_product_id_by_sku(sku)
        if not wc_product_id:
            continue

        line_items.append({
            "product_id": wc_product_id,
            "quantity": int(line["product_uom_qty"])
        })

    return {
        "payment_method": "bacs",
        "payment_method_title": "Transferencia",
        "set_paid": True,
        "billing": {
            "first_name": order["partner_id"][1] if order.get("partner_id") else "Cliente",
            "email": "test@example.com"
        },
        "line_items": line_items
    }


@router.post("/sync/orders")
def sync_orders():
    try:
        uid, models = connect_odoo()
        odoo_orders = get_odoo_orders(models, uid)

        processed_orders = load_processed()
        results = []

        for order in odoo_orders:

            # ✔ evitar duplicados persistentes
            if order["id"] in processed_orders:
                results.append({
                    "odoo_order": order["name"],
                    "status": "skipped"
                })
                continue

            wc_order = transform_odoo_to_wc(order, models, uid)

            wc_order["meta_data"] = [
                {
                    "key": "odoo_id",
                    "value": f"{order['id']}-{order['name']}"
                }
            ]

            response = wcapi.post("orders", data=wc_order)

            if response.status_code == 201:
                processed_orders.add(order["id"])
                status = "created"
            else:
                status = "error"

            results.append({
                "odoo_order": order["name"],
                "status": status
            })

        # ✔ guardar estado
        save_processed(processed_orders)

        return {
            "total": len(odoo_orders),
            "processed": len(processed_orders),
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))