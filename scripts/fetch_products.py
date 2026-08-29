import os, json, requests

with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line)

STORE = env['SHOPIFY_LIVE_STORE']
TOKEN = env['SHOPIFY_LIVE_STORE_ADMIN_TOKEN']
URL = f"https://{STORE}/admin/api/2026-01/graphql.json"

query = """
query($cursor: String) {
  products(first: 25, after: $cursor, query: "status:active") {
    pageInfo { hasNextPage endCursor }
    edges {
      node {
        title
        handle
        descriptionHtml
        vendor
        productType
        tags
        options { name values }
        images(first: 10) { edges { node { url altText } } }
        variants(first: 20) {
          edges {
            node {
              title
              price
              sku
              selectedOptions { name value }
              image { url }
            }
          }
        }
      }
    }
  }
}
"""

all_products = []
cursor = None
while True:
    resp = requests.post(URL, headers={
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json"
    }, json={"query": query, "variables": {"cursor": cursor}})
    data = resp.json()
    if "errors" in data:
        print("ERROR", data["errors"])
        break
    block = data["data"]["products"]
    for edge in block["edges"]:
        all_products.append(edge["node"])
    if block["pageInfo"]["hasNextPage"]:
        cursor = block["pageInfo"]["endCursor"]
    else:
        break

out_path = os.path.join(os.path.dirname(__file__), 'products_export.json')
with open(out_path, 'w') as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)

print(f"Fetched {len(all_products)} products -> {out_path}")
