from fastapi import APIRouter
from ...dependencies import wcapi

router = APIRouter()

@router.get("/orders/")
def get_subjects():
  try:
    response = wcapi.get("orders", params={"per_page": 10})
    if response.status_code == 200:
      orders = response.json()
      return orders
    else:
      print(f"Error {response.status_code}: {response.text}")
  except Exception as e:
    print(f"Connection error: {e}")

from fastapi import APIRouter
from ...dependencies import wcapi

router = APIRouter()

@router.get("/orders/")
def get_subjects():
  try:
    response = wcapi.get("orders", params={"per_page": 10})
    if response.status_code == 200:
      orders = response.json()
      return orders
    else:
      print(f"Error {response.status_code}: {response.text}")
  except Exception as e:
    print(f"Connection error: {e}")

  def order_exists_in_wc(odoo_id: int) -> bool:
    try:
        response = wcapi.get("orders", params={
            "meta_key": "odoo_id",
            "meta_value": odoo_id
        })
        return response.status_code == 200 and len(response.json()) > 0
    except:
        return False


@router.post("/sync-orders/")
def sync_orders():
    try:
        odoo_orders = get_odoo_orders()
        results = []

        for order in odoo_orders:

            # Evitar duplicados
            if order_exists_in_wc(order["id"]):
                results.append({
                    "odoo_order": order["name"],
                    "status": "skipped"
                })
                continue

            wc_order = transform_odoo_to_wc(order)

            # IMPORTANTE: guardar referencia de Odoo
            wc_order["meta_data"] = [
                {
                    "key": "odoo_id",
                    "value": order["id"]
                }
            ]

            response = wcapi.post("orders", data=wc_order)

            results.append({
                "odoo_order": order["name"],
                "status": "created" if response.status_code == 201 else "error"
            })

        return {
            "total": len(odoo_orders),
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

