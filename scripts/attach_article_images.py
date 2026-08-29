import os, json, requests

with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line)

STORE = env['SHOPIFY_DEV_STORE']
TOKEN = env['SHOPIFY_DEV_STORE_ADMIN_TOKEN']
URL = f"https://{STORE}/admin/api/2026-01/graphql.json"

articles = [
    {
        "id": "gid://shopify/Article/669520167160",  # גלי חום
        "image": "https://lh3.googleusercontent.com/aida-public/AB6AXuDtZVm6C6a-F2ujUNt9_uuShQta98RcjfZ0kHNuVKl0TlZHVRiHr9Ae59R9JVPGnPvjxyWdIT6U_C5iIWUAHDpqjEGByr6MZ4ey2lvXbfH022iEoD4ZnFa2fBIewH-z6AvXYzwtxaZZqRCU_xgAdyvGhlpPhVN0htYhchVsKD67D2PQVkH2zx-wd4zbaS12PigAwbwDxERxVgmSTdFBl9msJaH4Dtk108gp3JQO7DXE2_iYAnpnAGM",
    },
    {
        "id": "gid://shopify/Article/669520199928",  # 5 צמחי מרפא לשינה
        "image": "https://lh3.googleusercontent.com/aida-public/AB6AXuAqmzHIFloznvRMnq6IGBpfn99UfT8IMTHeO2l99GmkHaUyq2laj6U5DCNELjSI8zazzMbji9VJKaF1edojrQ5n6jyaT4oFUmHZ0Ko4z3I2RRd-mcDT5zyyGHSUwXXvvkHksnqwiEb87xzn-mDYoNAgR42OekxUDNRfMazcAd-tZzKRR2y0SxFJ11aeszF83UYonUFD1Ar-ltVHAsmqSU8tHproibxtOxF5kMazeNRMWbAh6aWWFyo",
    },
    {
        "id": "gid://shopify/Article/669520232696",  # אימוני כוח
        "image": "https://lh3.googleusercontent.com/aida-public/AB6AXuDWvgcc557FBCrB9Tt58TMK0R5Hm4tAbczVYQRIm9Lte6TkwwfxeKDlzEoik_p2SIG9LwAxiRMxHPZ0_paujj31KbFYWpm6FWJZFtGA99ykZQKnPU4acoTXGAnGMOMrQGkcvnpXRnlviW_uBE-bxunyEqnZLLos7n6cevkor0k_UT1eaAMsy3DKIUG3G-qkA0nK_auw0PHnOnUGBmWqNVNeqOF8m7MdQAJzOF5qvTe6eFuKzwqOk_I",
    },
    {
        "id": "gid://shopify/Article/669520265464",  # רצפת האגן
        "image": "https://lh3.googleusercontent.com/aida-public/AB6AXuAFFg395vLjCWNT3rGPEiglaXAKQmYKdbFCLeMojzEMWeFRsFndURskGQBGQumWe9cyTW1TVf2vHUKObWhZ-S3jPqC01yKIbS22WyfadbSPEbDXqNP3uDUKDxqQbXjTpPW_Jzc60HC_IMNz0kJBs44AZWQG1Ktm0BQjhAmDbJH896YNQ0MR26uU_uX_cjszBaeAFSfodiGIoe6a46NJC8MC8AJk2v-AjOJjKHIQpT_2An4ewUumONM",
    },
    {
        "id": "gid://shopify/Article/669520298232",  # איזון הורמונלי
        "image": "https://lh3.googleusercontent.com/aida-public/AB6AXuCGKIZb-x4tIjthL4rfJVXcUDi1nmES6sj9IH7DuclSAObfsbsL30nMQNw9GwJ1LBsftpYH6y2GgsxjCRQ6y-mweUVxEnk8eeRAVE2-8jzvfLjy5KPGaNNotdawd0rkNUtxqromBIfDS7csbfqVnq7gghAMc253CnGtrxsNTjqihzJNEK1PVwOzfI4wB6P47KB_y71JiwPv2cHPSjoHqeMDK7AqwX9mW3-rwAnOBkx68T-fvf625Rk",
    },
    {
        "id": "gid://shopify/Article/669520331000",  # פתרונות טבעיים לשינה
        "image": "https://lh3.googleusercontent.com/aida-public/AB6AXuAqmzHIFloznvRMnq6IGBpfn99UfT8IMTHeO2l99GmkHaUyq2laj6U5DCNELjSI8zazzMbji9VJKaF1edojrQ5n6jyaT4oFUmHZ0Ko4z3I2RRd-mcDT5zyyGHSUwXXvvkHksnqwiEb87xzn-mDYoNAgR42OekxUDNRfMazcAd-tZzKRR2y0SxFJ11aeszF83UYonUFD1Ar-ltVHAsmqSU8tHproibxtOxF5kMazeNRMWbAh6aWWFyo",
    },
]

MUTATION = """
mutation articleUpdate($id: ID!, $article: ArticleUpdateInput!) {
  articleUpdate(id: $id, article: $article) {
    article { title image { url } }
    userErrors { field message }
  }
}
"""

for a in articles:
    resp = requests.post(URL, headers={
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json"
    }, json={"query": MUTATION, "variables": {
        "id": a["id"],
        "article": {"image": {"url": a["image"]}}
    }})
    result = resp.json()
    errors = result.get("data", {}).get("articleUpdate", {}).get("userErrors", [])
    article = result.get("data", {}).get("articleUpdate", {}).get("article")
    if errors or not article:
        print("FAILED:", a["id"], errors or result.get("errors"))
    else:
        print("Updated:", article["title"])
