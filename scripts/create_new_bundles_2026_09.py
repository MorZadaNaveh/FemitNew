import os, json, requests

with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#') and line.strip())

STORE = env['SHOPIFY_LIVE_STORE']
TOKEN = env['SHOPIFY_LIVE_STORE_ADMIN_TOKEN']
URL = f"https://{STORE}/admin/api/2026-01/graphql.json"
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}


def gql(query, variables=None):
    r = requests.post(URL, headers=HEADERS, json={"query": query, "variables": variables or {}})
    data = r.json()
    if "errors" in data:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    return data["data"]


PRODUCT_SET = """
mutation productSet($input: ProductSetInput!) {
  productSet(input: $input, synchronous: true) {
    product { id title handle status variants(first: 10) { edges { node { title price } } } }
    userErrors { field message }
  }
}
"""


def create_product(input_data):
    result = gql(PRODUCT_SET, {"input": input_data})
    errors = result["productSet"]["userErrors"]
    if errors:
        print(f"[{input_data['title']}] ERRORS:", errors)
    else:
        p = result["productSet"]["product"]
        print(f"[{p['title']}] created: {p['id']} status={p['status']}")
        for v in p["variants"]["edges"]:
            print("   ", v["node"]["title"], v["node"]["price"])
    return result["productSet"]["product"]


def d(n):
    return f"{round(n, 2):.2f}"


# ---------------------------------------------------------------------------
# Bundle 1: ערכת וסת — תחתוני וסת כותנה (fixed) + גביעונית/דיסק (choice)
# ---------------------------------------------------------------------------
UNDERWEAR = 144.00
CUP = 160.00
DISC = 210.00

bundle1 = {
    "title": "ערכת וסת",
    "descriptionHtml": (
        "<p>ערכת וסת נוחה - תחתוני וסת מכותנה בשילוב מוצר וסת לבחירתך, "
        "ב-10% הנחה ממחיר הרכישה הנפרדת.</p>"
        "<ul>"
        "<li><strong>תחתוני וסת - כותנה</strong></li>"
        "<li><strong>גביעונית וסת רוביקאפ או דיסק וסת Hello Period</strong> - לבחירתך</li>"
        "</ul>"
    ),
    "status": "DRAFT",
    "tags": ["all", "Period", "וסת", "bundle"],
    "productOptions": [
        {"name": "תוספת לבחירה", "values": [
            {"name": "גביעונית וסת - רוביקאפ"},
            {"name": "דיסק וסת Hello Period"},
        ]},
    ],
    "variants": [
        {"price": d((UNDERWEAR + CUP) * 0.9), "optionValues": [{"optionName": "תוספת לבחירה", "name": "גביעונית וסת - רוביקאפ"}]},
        {"price": d((UNDERWEAR + DISC) * 0.9), "optionValues": [{"optionName": "תוספת לבחירה", "name": "דיסק וסת Hello Period"}]},
    ],
}
create_product(bundle1)

# ---------------------------------------------------------------------------
# Bundle 2: ערכת ספרים - מילים הורגות וכלואות
# ---------------------------------------------------------------------------
MILIM_HORGOT = 98.00
KLUOT = 82.00

bundle2 = {
    "title": "ערכת ספרים: מילים הורגות וכלואות",
    "descriptionHtml": (
        "<p>שני ספרים על אלימות כלפי נשים בזוגיות, ב-10% הנחה ממחיר הרכישה הנפרדת.</p>"
        "<ul>"
        "<li><strong>מילים הורגות</strong> - ניני גוטספלד-מנוח</li>"
        "<li><strong>כלואות - שתלטנות קיצונית בזוגיות</strong> - ד״ר אילנה קוורטין</li>"
        "</ul>"
    ),
    "status": "DRAFT",
    "tags": ["all", "Books", "ספרים", "אלימות", "bundle"],
    "productOptions": [
        {"name": "Title", "values": [{"name": "Default Title"}]},
    ],
    "variants": [
        {"price": d((MILIM_HORGOT + KLUOT) * 0.9), "optionValues": [{"optionName": "Title", "name": "Default Title"}]},
    ],
}
create_product(bundle2)

# ---------------------------------------------------------------------------
# Bundle 3: EDIT existing ערכת טיולים — drop the book, apply 10% discount
# ---------------------------------------------------------------------------
TRIP_PRODUCT_ID = "gid://shopify/Product/8398067040330"
UNDERWEAR_ZH = 122.00
FUNNEL = 42.00
pants_prices = {
    "מכנסי טייץ ארוכים": 329.00,
    "מכנסי טייץ קצרים": 244.00,
    "מכנסי שטח ארוכים": 399.00,
    "מכנסי שטח קצרים": 258.00,
}

PRODUCT_UPDATE = """
mutation productUpdate($input: ProductInput!) {
  productUpdate(input: $input) {
    product { id title }
    userErrors { field message }
  }
}
"""
new_description = (
    "<p>ערכת טיולים לנשים - כל מה שצריך כדי לצאת לדרך בראש שקט, "
    "ב-10% הנחה ממחיר הרכישה הנפרדת.</p>"
    "<ul>"
    "<li><strong>מכנסי טיולים</strong> ZipHers - בחרי סוג ומידה</li>"
    "<li><strong>תחתוני ZipHers</strong> - בחרי מידה</li>"
    "<li><strong>משפך להטלת שתן בעמידה</strong> לנשים</li>"
    "</ul>"
)
result = gql(PRODUCT_UPDATE, {"input": {"id": TRIP_PRODUCT_ID, "descriptionHtml": new_description}})
print("ערכת טיולים description update:", result["productUpdate"]["userErrors"] or "OK")

# fetch current variants to build the bulk price update
VARIANTS_QUERY = """
query($id: ID!, $cursor: String) {
  product(id: $id) {
    variants(first: 100, after: $cursor) {
      edges { cursor node { id selectedOptions { name value } } }
      pageInfo { hasNextPage }
    }
  }
}
"""
all_variants = []
cursor = None
while True:
    data = gql(VARIANTS_QUERY, {"id": TRIP_PRODUCT_ID, "cursor": cursor})
    edges = data["product"]["variants"]["edges"]
    all_variants.extend(edges)
    if not data["product"]["variants"]["pageInfo"]["hasNextPage"]:
        break
    cursor = edges[-1]["cursor"]

variant_updates = []
for e in all_variants:
    n = e["node"]
    pants_value = n["selectedOptions"][0]["value"]
    pants_type = pants_value.split(" - ")[0]
    new_price = d((pants_prices[pants_type] + UNDERWEAR_ZH + FUNNEL) * 0.9)
    variant_updates.append({"id": n["id"], "price": new_price})

BULK_UPDATE = """
mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    productVariants { id price }
    userErrors { field message }
  }
}
"""
# Shopify limits bulk variant mutations; chunk into batches of 50
for i in range(0, len(variant_updates), 50):
    chunk = variant_updates[i:i + 50]
    result = gql(BULK_UPDATE, {"productId": TRIP_PRODUCT_ID, "variants": chunk})
    errs = result["productVariantsBulkUpdate"]["userErrors"]
    print(f"ערכת טיולים variant price batch {i}-{i+len(chunk)}:", errs or "OK")

# ---------------------------------------------------------------------------
# Bundle 4: ערכת ספרים לבחירה — combos of 3 books / 3 books + card
# ---------------------------------------------------------------------------
MITOS_HAYOFI = 88.00
HEDER_MISHELACH = 94.00
EICH_KORIM_LACH = 96.00
QUEENG = 50.00

combos = [
    ("מיתוס היופי + חדר משלך", MITOS_HAYOFI + HEDER_MISHELACH),
    ("מיתוס היופי + אז איך קוראים לך עכשיו", MITOS_HAYOFI + EICH_KORIM_LACH),
    ("חדר משלך + אז איך קוראים לך עכשיו", HEDER_MISHELACH + EICH_KORIM_LACH),
    ("מיתוס היופי + חדר משלך + אז איך קוראים לך עכשיו", MITOS_HAYOFI + HEDER_MISHELACH + EICH_KORIM_LACH),
    ("מיתוס היופי + חדר משלך + קלפי QueenG", MITOS_HAYOFI + HEDER_MISHELACH + QUEENG),
    ("מיתוס היופי + אז איך קוראים לך עכשיו + קלפי QueenG", MITOS_HAYOFI + EICH_KORIM_LACH + QUEENG),
    ("חדר משלך + אז איך קוראים לך עכשיו + קלפי QueenG", HEDER_MISHELACH + EICH_KORIM_LACH + QUEENG),
]

bundle4 = {
    "title": "ערכת ספרים לבחירה",
    "descriptionHtml": (
        "<p>בחרי כל שילוב של שני ספרים, שלושה ספרים, או שני ספרים וקלפי משחק - "
        "ב-10% הנחה ממחיר הרכישה הנפרדת.</p>"
        "<ul>"
        "<li><strong>מיתוס היופי</strong> - נעמי וולף</li>"
        "<li><strong>חדר משלך</strong> - וירג׳יניה וולף</li>"
        "<li><strong>אז איך קוראים לך עכשיו?</strong> - מיכל רום</li>"
        "<li><strong>קלפי משחק לא ממוגדרים QueenG</strong> (בשילוב עם שני ספרים)</li>"
        "</ul>"
    ),
    "status": "DRAFT",
    "tags": ["all", "Books", "ספרים", "bundle"],
    "productOptions": [
        {"name": "בחירת ערכה", "values": [{"name": c[0]} for c in combos]},
    ],
    "variants": [
        {"price": d(price * 0.9), "optionValues": [{"optionName": "בחירת ערכה", "name": name}]}
        for name, price in combos
    ],
}
create_product(bundle4)

# ---------------------------------------------------------------------------
# Bundle 5a: new fan product (מניפה לגלי חום), DRAFT
# ---------------------------------------------------------------------------
fan_product = {
    "title": "מניפה לגלי חום",
    "descriptionHtml": "<p>מניפה קומפקטית וקלה לרגעי גלי חום, נוחה לנשיאה בתיק.</p>",
    "status": "DRAFT",
    "tags": ["all", "Menopause", "גיל המעבר", "אביזרים"],
    "productOptions": [
        {"name": "Title", "values": [{"name": "Default Title"}]},
    ],
    "variants": [
        {"price": "39.00", "optionValues": [{"optionName": "Title", "name": "Default Title"}]},
    ],
}
fan = create_product(fan_product)
FAN_PRICE = 39.00

# ---------------------------------------------------------------------------
# Bundle 5b: ערכת גיל המעבר - ספר ומניפה
# ---------------------------------------------------------------------------
MENOPAUSE_BOOK = 98.00

bundle5 = {
    "title": "ערכת גיל המעבר: ספר ומניפה",
    "descriptionHtml": (
        "<p>ספר המדריך המקיף לגיל המעבר בשילוב מניפה לרגעי גלי חום, "
        "ב-10% הנחה ממחיר הרכישה הנפרדת.</p>"
        "<ul>"
        "<li><strong>כל מה שאת חייבת לדעת על גיל המעבר</strong> - ד״ר ג׳ן גונטר</li>"
        "<li><strong>מניפה לגלי חום</strong></li>"
        "</ul>"
    ),
    "status": "DRAFT",
    "tags": ["all", "Menopause", "גיל המעבר", "bundle"],
    "productOptions": [
        {"name": "Title", "values": [{"name": "Default Title"}]},
    ],
    "variants": [
        {"price": d((MENOPAUSE_BOOK + FAN_PRICE) * 0.9), "optionValues": [{"optionName": "Title", "name": "Default Title"}]},
    ],
}
create_product(bundle5)

# ---------------------------------------------------------------------------
# Bundle 6: ערכת אינטימיות — vibrator choice + lubricant 500ml (fixed)
# ---------------------------------------------------------------------------
VIBRATOR_1 = 289.00  # ויברטור יונק סטיספייר פרו 2 דור 2 (ברונזה/לילך)
VIBRATOR_2 = 268.00  # ויברטור רוטט חיצוני מתלבש עם אפליקציה - סטיספייר
LUBE_500 = 175.00

vib_options = [
    ("ויברטור יונק פרו 2 דור 2 - ברונזה", VIBRATOR_1),
    ("ויברטור יונק פרו 2 דור 2 - לילך", VIBRATOR_1),
    ("ויברטור רוטט חיצוני מתלבש עם אפליקציה", VIBRATOR_2),
]

bundle6 = {
    "title": "ערכת אינטימיות",
    "descriptionHtml": (
        "<p>ויברטור לבחירתך בשילוב חומר סיכוך בגודל 500 מ״ל, "
        "ב-10% הנחה ממחיר הרכישה הנפרדת.</p>"
        "<ul>"
        "<li><strong>ויברטור</strong> - יונק סטיספייר פרו 2 דור 2 או רוטט חיצוני מתלבש עם אפליקציה, לבחירתך</li>"
        "<li><strong>ID Glide ג'ל סיכוך על בסיס מים</strong> - 500 מ״ל</li>"
        "</ul>"
    ),
    "status": "DRAFT",
    "tags": ["all", "Sexuality", "אינטימיות", "bundle"],
    "productOptions": [
        {"name": "בחירת ויברטור", "values": [{"name": v[0]} for v in vib_options]},
    ],
    "variants": [
        {"price": d((price + LUBE_500) * 0.9), "optionValues": [{"optionName": "בחירת ויברטור", "name": name}]}
        for name, price in vib_options
    ],
}
create_product(bundle6)
