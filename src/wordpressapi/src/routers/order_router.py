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
