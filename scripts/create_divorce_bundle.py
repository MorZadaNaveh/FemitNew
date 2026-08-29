import os, json, requests

with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line)

STORE = env['SHOPIFY_LIVE_STORE']
TOKEN = env['SHOPIFY_LIVE_STORE_ADMIN_TOKEN']
URL = f"https://{STORE}/admin/api/2026-01/graphql.json"

VIBRATOR_PRICE = 289.00
BOOK_PRICE = 94.00
TOTAL_PRICE = round(VIBRATOR_PRICE + BOOK_PRICE, 2)
colors = ["ברונזה", "לילך"]

description = (
    "<p>ערכה למי שבוחרת בעצמה - כל מה שצריך כדי לחגוג עצמאות, הנאה וזמן איכות עם עצמך, "
    "במחיר המוצרים המקוריים בלבד ללא תוספת.</p>"
    "<ul>"
    "<li><strong>ויברטור יונק סטיספייר פרו 2</strong> - בחרי צבע</li>"
    "<li><strong>חדר משלך</strong> - וירג׳יניה וולף</li>"
    "</ul>"
)

input_data = {
    "title": "ערכת עצמאות",
    "descriptionHtml": description,
    "status": "DRAFT",
    "tags": ["all", "sex", "מיניות", "bundle"],
    "productOptions": [
        {"name": "צבע ויברטור", "values": [{"name": c} for c in colors]},
    ],
    "variants": [
        {"price": f"{TOTAL_PRICE:.2f}", "optionValues": [{"optionName": "צבע ויברטור", "name": c}]}
        for c in colors
    ],
}

MUTATION = """
mutation productSet($input: ProductSetInput!) {
  productSet(input: $input, synchronous: true) {
    product { id title handle status variants(first: 5) { edges { node { title price } } } }
    userErrors { field message }
  }
}
"""

resp = requests.post(URL, headers={
    "X-Shopify-Access-Token": TOKEN,
    "Content-Type": "application/json"
}, json={"query": MUTATION, "variables": {"input": input_data}})
result = resp.json()
print(json.dumps(result, ensure_ascii=False, indent=2))
