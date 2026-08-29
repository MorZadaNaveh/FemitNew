import os, json, time, requests

with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line)

STORE = env['SHOPIFY_DEV_STORE']
TOKEN = env['SHOPIFY_DEV_STORE_ADMIN_TOKEN']
URL = f"https://{STORE}/admin/api/2026-01/graphql.json"
ONLINE_STORE_PUBLICATION_ID = "gid://shopify/Publication/212112277752"

LIST_QUERY = """
{ products(first: 50) { edges { node { id title } } } }
"""

PUBLISH_MUTATION = """
mutation publishablePublish($id: ID!, $input: [PublicationInput!]!) {
  publishablePublish(id: $id, input: $input) {
    publishable { ... on Product { id } }
    userErrors { field message }
  }
}
"""

def post(query, variables=None):
    resp = requests.post(URL, headers={
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json"
    }, json={"query": query, "variables": variables or {}})
    return resp.json()

products = post(LIST_QUERY)["data"]["products"]["edges"]
print(f"Found {len(products)} products")

for edge in products:
    pid = edge["node"]["id"]
    title = edge["node"]["title"]
    result = post(PUBLISH_MUTATION, {
        "id": pid,
        "input": [{"publicationId": ONLINE_STORE_PUBLICATION_ID}]
    })
    errors = result.get("data", {}).get("publishablePublish", {}).get("userErrors", [])
    if errors:
        print("FAILED:", title, errors)
    else:
        print("Published:", title)
    time.sleep(0.3)
