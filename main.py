from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import httpx, os, asyncio

# optional sync deps used as fallback
import requests
from requests_oauthlib import OAuth1

load_dotenv()

WC_URL    = os.getenv("WC_URL")
WC_KEY    = os.getenv("WC_CONSUMER_KEY")
WC_SECRET = os.getenv("WC_CONSUMER_SECRET")
WC_API    = f"{WC_URL}/wp-json/wc/v3"

app = FastAPI(title="API Productos WooCommerce")


@app.get("/productos")
async def get_productos(page: int = 1, per_page: int = 20):
    # First attempt: async request with basic auth (httpx)
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            f"{WC_API}/products",
            auth=(WC_KEY, WC_SECRET),
            params={"page": page, "per_page": per_page},
        )

    # If basic auth worked, use that response
    if response.status_code == 200:
        json_data = response.json()
        headers = response.headers
    else:
        # Fallback: try OAuth1-signed request (some WooCommerce setups require OAuth1 over HTTP)
        def oauth_call():
            return requests.get(
                f"{WC_API}/products",
                auth=OAuth1(WC_KEY, WC_SECRET),
                params={"page": page, "per_page": per_page},
                verify=False,
                timeout=10,
            )

        r = await asyncio.to_thread(oauth_call)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail="Error al obtener productos")
        json_data = r.json()
        headers = r.headers

    productos = [
        {
            "id":          p["id"],
            "nombre":      p["name"],
            "descripcion": p.get("short_description") or p.get("description"),
            "precio":      p.get("price"),
            "stock":       p.get("stock_status"),
            "imagen":      p.get("images")[0].get("src") if p.get("images") else None,
            "categorias":  [c["name"] for c in p.get("categories", [])],
        }
        for p in json_data
    ]

    return {
        "productos":    productos,
        "total":        headers.get("X-WP-Total"),
        "total_paginas": headers.get("X-WP-TotalPages"),
        "pagina":       page,
        "por_pagina":   per_page,
    }