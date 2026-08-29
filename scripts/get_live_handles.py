import os, json, requests

with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line)

STORE = env['SHOPIFY_LIVE_STORE']
TOKEN = env['SHOPIFY_LIVE_STORE_ADMIN_TOKEN']
URL = f"https://{STORE}/admin/api/2026-01/graphql.json"

titles = [
    "גביעונית וסת - רוביקאפ",
    "תחתוני וסת - כותנה",
    "דיסק וסת Hello Period",
    "טרום וגיל המעבר: כל מה שאת חייבת לדעת - ולא היה לך את מי לשאול",
    "ויברטור יונק סטיספייר פרו 2 דור 2",
    "ויברטור רוטט חיצוני מתלבש עם אפליקציה - סטיספייר",
    "ID Glide ג'ל סיכוך על בסיס מים",
    "חדר משלך - וירג׳יניה וולף",
    "כל מה שאת חייבת לדעת על גיל המעבר - ד״ר ג׳ן גונטר",
    "מילים הורגות - ניני גוטספלד-מנוח",
    "פורום מיכל סלה",
    "האור שבפנים - תמי אביגיא",
    "כלואות - שתלטנות קיצונית בזוגיות - ד״ר אילנה קוורטין",
    "אני רוצה לשבור את הקירות! - ד״ר אילנה קוורטין",
    'חומר סיכוך ID Pleasure ‏130 מ"ל',
]

query = """
{ products(first: 250) { edges { node { title handle status } } } }
"""

resp = requests.post(URL, headers={
    "X-Shopify-Access-Token": TOKEN,
    "Content-Type": "application/json"
}, json={"query": query})
result = resp.json()
all_products = {e["node"]["title"]: e["node"]["handle"] for e in result["data"]["products"]["edges"]}

for t in titles:
    handle = all_products.get(t)
    print(json.dumps(t, ensure_ascii=False), "->", handle)
