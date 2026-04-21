from fastapi import FastAPI, HTTPException
from fastapi import APIRouter
from ...dependencies import wcapi


WC_URL    = wcapi.url
WC_KEY    = wcapi.consumer_key
WC_SECRET = wcapi.consumer_secret
WC_API    = f"{WC_URL}/wp-json/wc/v3"

router = APIRouter()

@router.get("/products")
async def get_productos(page: int = 1, per_page: int = 20):
    response = await wcapi.get(
        f"{WC_API}/products",
        auth=(WC_KEY, WC_SECRET),
        params={"page": page, "per_page": per_page}
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al obtener productos")

    productos = [
        {
            "id":          p["id"],
            "nombre":      p["name"],
            "descripcion": p["short_description"] or p["description"],
            "precio":      p["price"],
            "stock":       p["stock_status"],
            "imagen":      p["images"][0]["src"] if p["images"] else None,
            "categorias":  [c["name"] for c in p["categories"]],
        }
        for p in response.json()
    ]

    return {
        "productos":    productos,
        "total":        response.headers.get("X-WP-Total"),
        "total_paginas": response.headers.get("X-WP-TotalPages"),
        "pagina":       page,
        "por_pagina":   per_page,
    }