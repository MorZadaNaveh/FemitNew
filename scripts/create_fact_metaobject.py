import os, json, sys, requests

with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))

TARGET = sys.argv[1] if len(sys.argv) > 1 else "dev"
if TARGET == "dev":
    STORE = env['SHOPIFY_DEV_STORE']
    TOKEN = env['SHOPIFY_DEV_STORE_ADMIN_TOKEN']
else:
    STORE = env['SHOPIFY_LIVE_STORE']
    TOKEN = env['SHOPIFY_LIVE_STORE_ADMIN_TOKEN']

URL = f"https://{STORE}/admin/api/2026-01/graphql.json"
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

# Facts are created as DRAFT (invisible on storefront) until this is flipped to
# "ACTIVE" and the script re-run (or existing entries updated via metaobjectUpdate).
FACT_STATUS = "DRAFT"


def gql(query, variables=None):
    r = requests.post(URL, headers=HEADERS, json={"query": query, "variables": variables or {}})
    data = r.json()
    if "errors" in data:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    return data["data"]


DEFINITION_MUTATION = """
mutation metaobjectDefinitionCreate($definition: MetaobjectDefinitionCreateInput!) {
  metaobjectDefinitionCreate(definition: $definition) {
    metaobjectDefinition { id type }
    userErrors { field message code }
  }
}
"""

definition_input = {
    "definition": {
        "type": "daily_fact",
        "name": "Fact",
        "capabilities": {"publishable": {"enabled": True}},
        "fieldDefinitions": [
            {"key": "sentence", "name": "Sentence", "type": "multi_line_text_field", "required": True},
            {"key": "link", "name": "Link", "type": "url", "required": False},
        ],
    }
}

result = gql(DEFINITION_MUTATION, definition_input)
errors = result["metaobjectDefinitionCreate"]["userErrors"]
if errors:
    print(f"[{TARGET}] definition errors:", errors)
else:
    print(f"[{TARGET}] definition created:", result["metaobjectDefinitionCreate"]["metaobjectDefinition"])

CREATE_MUTATION = """
mutation metaobjectCreate($metaobject: MetaobjectCreateInput!) {
  metaobjectCreate(metaobject: $metaobject) {
    metaobject { id handle }
    userErrors { field message code }
  }
}
"""

facts = [
    "גיל המעבר הממוצע מתרחש סביב גיל 51, אך התהליך עצמו (פרימנופאוזה) יכול להימשך שנים לפני כן.",
    "צפיפות העצם אצל נשים יכולה לרדת בעד 20% בחמש השנים הראשונות שלאחר גיל המעבר, מה שהופך פעילות גופנית נושאת משקל לחשובה במיוחד.",
    "רצפת האגן היא קבוצת שרירים שניתן לחזק בכל גיל - תרגילי קגל יכולים לשפר שליטה על שלפוחית השתן תוך מספר שבועות.",
]

for sentence in facts:
    payload = {
        "metaobject": {
            "type": "daily_fact",
            "capabilities": {"publishable": {"status": FACT_STATUS}},
            "fields": [{"key": "sentence", "value": sentence}],
        }
    }
    res = gql(CREATE_MUTATION, payload)
    errs = res["metaobjectCreate"]["userErrors"]
    if errs:
        print(f"[{TARGET}] fact create errors:", errs)
    else:
        print(f"[{TARGET}] fact created:", res["metaobjectCreate"]["metaobject"])
