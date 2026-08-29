import os, json, time, requests

with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line)

STORE = env['SHOPIFY_DEV_STORE']
TOKEN = env['SHOPIFY_DEV_STORE_ADMIN_TOKEN']
URL = f"https://{STORE}/admin/api/2026-01/graphql.json"

with open(os.path.join(os.path.dirname(__file__), 'products_export.json')) as f:
    products = json.load(f)

SET_MUTATION = """
mutation productSet($input: ProductSetInput!) {
  productSet(input: $input, synchronous: true) {
    product { id title handle }
    userErrors { field message }
  }
}
"""

FILES_MUTATION = """
mutation productSet($input: ProductSetInput!) {
  productSet(input: $input, synchronous: true) {
    product { id }
    userErrors { field message }
  }
}
"""

def post(query, variables):
    resp = requests.post(URL, headers={
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json"
    }, json={"query": query, "variables": variables})
    return resp.json()

created = []
failed = []

for p in products:
    options = p.get("options", [])
    # Shopify default single-variant products have one option "Title"/"כותרת" with value "Default Title" - skip options in that case
    has_real_options = not (len(options) == 1 and options[0]["values"] == ["Default Title"])

    variants_input = []
    for v in p["variants"]["edges"]:
        node = v["node"]
        variant = {"price": node["price"] or "0.00"}
        if node.get("sku"):
            variant["sku"] = node["sku"]
        if has_real_options:
            variant["optionValues"] = [
                {"optionName": so["name"], "name": so["value"]}
                for so in node["selectedOptions"]
            ]
        else:
            variant["optionValues"] = []
        variants_input.append(variant)

    input_data = {
        "title": p["title"],
        "descriptionHtml": p["descriptionHtml"] or "",
        "vendor": p["vendor"] or "",
        "productType": p["productType"] or "",
        "tags": p["tags"],
        "status": "ACTIVE",
        "variants": variants_input,
    }
    if has_real_options:
        input_data["productOptions"] = [
            {"name": o["name"], "values": [{"name": v} for v in o["values"]]}
            for o in options
        ]
    else:
        input_data["productOptions"] = [
            {"name": "Title", "values": [{"name": "Default Title"}]}
        ]
        variants_input[0]["optionValues"] = [{"optionName": "Title", "name": "Default Title"}]

    result = post(SET_MUTATION, {"input": input_data})
    errors = result.get("data", {}).get("productSet", {}).get("userErrors", [])
    product = result.get("data", {}).get("productSet", {}).get("product")

    if errors or not product:
        print("FAILED:", p["title"], errors or result.get("errors"))
        failed.append(p["title"])
        continue

    # Attach images in a second call
    image_urls = [img["node"]["url"] for img in p["images"]["edges"]][:10]
    if image_urls:
        files_input = {
            "id": product["id"],
            "files": [{"originalSource": url, "contentType": "IMAGE"} for url in image_urls]
        }
        img_result = post(FILES_MUTATION, {"input": files_input})
        img_errors = img_result.get("data", {}).get("productSet", {}).get("userErrors", [])
        if img_errors:
            print("  (image warning for", p["title"], "):", img_errors)

    print("Created:", product["title"], "->", product["handle"])
    created.append({"title": product["title"], "handle": product["handle"], "id": product["id"]})
    time.sleep(0.5)

print(f"\nDone. {len(created)} created, {len(failed)} failed.")
if failed:
    print("Failed:", failed)

with open(os.path.join(os.path.dirname(__file__), 'imported_products.json'), 'w') as f:
    json.dump(created, f, ensure_ascii=False, indent=2)
