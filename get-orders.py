from woocommerce import API

wcapi = API(
    url="http://localhost:8080",
    consumer_key="",
    consumer_secret="",
    version="wc/v3",
    timeout=20
)

try:
    response = wcapi.get("orders", params={"per_page": 10})
    if response.status_code == 200:
        orders = response.json()
        print(f"{len(orders)} orders found")
        count = 0
        for p in orders:
            print(f"Order #{count}")
            print(f"id: {p['id']}")
            print(f"parent_id: {p['parent_id']}")
            print(f"number: {p['number']}")
            print(f"status: {p['status']}")
            print(f"currency: {p['currency']}")
            print(f"date_created: {p['date_created']}")
            print(f"total: {p['total']}")
            print(f"shipping: {p['shipping']}")
            print(f"billing: {p['billing']}")
            print(f"line_items: {p['line_items']}")
            print("")
            count += 1
    else:
        print(f"Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"Connection error: {e}")