import os, json, requests

with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line)

STORE = env['SHOPIFY_DEV_STORE']
TOKEN = env['SHOPIFY_DEV_STORE_ADMIN_TOKEN']
URL = f"https://{STORE}/admin/api/2026-01/graphql.json"

id_map = {
    "גביעונית וסת - רוביקאפ": "gid://shopify/Product/10272431636728",
    "תחתוני וסת - כותנה": "gid://shopify/Product/10272431669496",
    "משפך להטלת שתן בעמידה לנשים": "gid://shopify/Product/10272431735032",
    "דיסק וסת Hello Period": "gid://shopify/Product/10272431800568",
    "ויברטור יונק סטיספייר פרו 2 דור 2": "gid://shopify/Product/10272431866104",
    "מכנסי טייץ ארוכים ZipHers": "gid://shopify/Product/10272431898872",
    "כל מה שאת חייבת לדעת על גיל המעבר - ד״ר ג׳ן גונטר": "gid://shopify/Product/10272431931640",
    "מכנסי טייץ קצרים ZipHers": "gid://shopify/Product/10272431997176",
    "מכנסי שטח ארוכים ZipHers": "gid://shopify/Product/10272432029944",
    "מכנסי שטח קצרים של ZipHers": "gid://shopify/Product/10272432062712",
    "תחתוני ZipHers": "gid://shopify/Product/10272432095480",
    "חומר סיכוך ID Pleasure ‏130 מ\"ל": "gid://shopify/Product/10272432128248",
    "ID Glide ג'ל סיכוך על בסיס מים": "gid://shopify/Product/10272432193784",
    "טרום וגיל המעבר: כל מה שאת חייבת לדעת - ולא היה לך את מי לשאול": "gid://shopify/Product/10272432881912",
    "ויברטור רוטט חיצוני מתלבש עם אפליקציה - סטיספייר": "gid://shopify/Product/10272433176824",
}

collections = [
    {
        "title": "ציוד לטיולים",
        "description": "כל מה שצריך כדי לצאת לדרך בראש שקט - מבגדים פונקציונליים ועד פתרונות נוחות לשעות ארוכות בחוץ.",
        "products": [
            "מכנסי טייץ ארוכים ZipHers",
            "מכנסי טייץ קצרים ZipHers",
            "מכנסי שטח ארוכים ZipHers",
            "מכנסי שטח קצרים של ZipHers",
            "תחתוני ZipHers",
            "משפך להטלת שתן בעמידה לנשים",
        ],
    },
    {
        "title": "תמיכה בגיל המעבר ובפוריות",
        "description": "מוצרים ומידע התומכים בנשים בגילאי 35 ומעלה - בין אם את מתמודדת עם תסמיני גיל המעבר, מנסה להיכנס להריון, או פשוט רוצה להכיר את הגוף שלך טוב יותר. הגוף הנשי משתנה לאורך כל החיים, וכל שלב ראוי להתייחסות ולתמיכה מותאמת.",
        "products": [
            "חומר סיכוך ID Pleasure ‏130 מ\"ל",
            "ID Glide ג'ל סיכוך על בסיס מים",
            "כל מה שאת חייבת לדעת על גיל המעבר - ד״ר ג׳ן גונטר",
            "טרום וגיל המעבר: כל מה שאת חייבת לדעת - ולא היה לך את מי לשאול",
            "ויברטור רוטט חיצוני מתלבש עם אפליקציה - סטיספייר",
        ],
    },
    {
        "title": "מוצרי וסת",
        "description": "פתרונות וסת נוחים, בריאים וברי-קיימא - לכל זרימה ולכל שלב בחיים.",
        "products": [
            "גביעונית וסת - רוביקאפ",
            "תחתוני וסת - כותנה",
            "דיסק וסת Hello Period",
        ],
    },
]

CREATE = """
mutation collectionCreate($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection { id title handle }
    userErrors { field message }
  }
}
"""

for c in collections:
    product_ids = [id_map[t] for t in c["products"]]
    resp = requests.post(URL, headers={
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json"
    }, json={"query": CREATE, "variables": {"input": {
        "title": c["title"],
        "descriptionHtml": f"<p>{c['description']}</p>",
        "products": product_ids,
    }}})
    result = resp.json()
    errors = result.get("data", {}).get("collectionCreate", {}).get("userErrors", [])
    collection = result.get("data", {}).get("collectionCreate", {}).get("collection")
    if errors or not collection:
        print("FAILED:", c["title"], errors or result.get("errors"))
    else:
        print("Created:", collection["title"], "->", collection["handle"], f"({len(product_ids)} products)")
