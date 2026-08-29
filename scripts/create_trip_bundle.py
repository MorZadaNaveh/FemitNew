import os, json, requests

with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line)

STORE = env['SHOPIFY_LIVE_STORE']
TOKEN = env['SHOPIFY_LIVE_STORE_ADMIN_TOKEN']
URL = f"https://{STORE}/admin/api/2026-01/graphql.json"

# Real component prices (as fetched from live store)
UNDERWEAR_PRICE = 122.00
FUNNEL_PRICE = 42.00
BOOK_PRICE = 98.00
FIXED_ADDON = UNDERWEAR_PRICE + FUNNEL_PRICE + BOOK_PRICE

pants_types = [
    {"label": "מכנסי טייץ ארוכים", "price": 329.00, "sizes": ["M", "L", "XL"]},
    {"label": "מכנסי טייץ קצרים", "price": 244.00, "sizes": ["XS", "S", "M", "L", "XL", "2XL"]},
    {"label": "מכנסי שטח ארוכים", "price": 399.00, "sizes": ["M", "L", "XL"]},
    {"label": "מכנסי שטח קצרים", "price": 258.00, "sizes": ["XS", "S", "M", "L", "XL", "2XL"]},
]
underwear_sizes = ["XS", "S", "M", "L", "XL", "2XL"]

pants_option_values = []
for pt in pants_types:
    for size in pt["sizes"]:
        pants_option_values.append(f'{pt["label"]} - {size}')

variants = []
for pt in pants_types:
    for size in pt["sizes"]:
        pants_value = f'{pt["label"]} - {size}'
        price = round(pt["price"] + FIXED_ADDON, 2)
        for u_size in underwear_sizes:
            variants.append({
                "price": f"{price:.2f}",
                "optionValues": [
                    {"optionName": "מכנסיים", "name": pants_value},
                    {"optionName": "מידת תחתונים", "name": u_size},
                ]
            })

description = (
    "<p>ערכת טיולים מלאה לנשים - כל מה שצריך כדי לצאת לדרך בראש שקט, "
    "במחיר המוצרים המקוריים בלבד ללא תוספת.</p>"
    "<ul>"
    "<li><strong>מכנסי טיולים</strong> ZipHers - בחרי סוג ומידה</li>"
    "<li><strong>תחתוני ZipHers</strong> - בחרי מידה</li>"
    "<li><strong>משפך להטלת שתן בעמידה</strong> לנשים</li>"
    "<li><strong>ספר מלווה לדרך:</strong> \"כל מה שאת חייבת לדעת על גיל המעבר\" - ד״ר ג׳ן גונטר</li>"
    "</ul>"
)

input_data = {
    "title": "ערכת טיולים",
    "descriptionHtml": description,
    "status": "DRAFT",
    "tags": ["all", "Travel", "Trip", "טיולים", "bundle"],
    "productOptions": [
        {"name": "מכנסיים", "values": [{"name": v} for v in pants_option_values]},
        {"name": "מידת תחתונים", "values": [{"name": v} for v in underwear_sizes]},
    ],
    "variants": variants,
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
