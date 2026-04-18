from fastapi import APIRouter, HTTPException
from woocommerce import API
from ...dependencies import wcapi

router = APIRouter()

@router.get("/subjects/")
def get_subjects():
  try:
    response = wcapi.get("orders", params={"per_page": 10})
    if response.status_code == 200:
      orders = response.json()
    else:
      print(f"Error {response.status_code}: {response.text}")
  except Exception as e:
    print(f"Connection error: {e}")
    return orders
