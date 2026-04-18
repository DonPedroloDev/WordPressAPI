from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import httpx, os

load_dotenv()

WC_URL    = os.getenv("WC_URL")
WC_KEY    = os.getenv("WC_CONSUMER_KEY")
WC_SECRET = os.getenv("WC_CONSUMER_SECRET")
WC_API    = f"{WC_URL}/wp-json/wc/v3"

app = FastAPI(title="API Productos WooCommerce")

@app.get("/productos")
async def get_productos(page: int = 1, per_page: int = 20):
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
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