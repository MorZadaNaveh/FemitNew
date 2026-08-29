import os, json, requests

with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line)

STORE = env['SHOPIFY_DEV_STORE']
TOKEN = env['SHOPIFY_DEV_STORE_ADMIN_TOKEN']
BLOG_ID = "gid://shopify/Blog/107395186936"
URL = f"https://{STORE}/admin/api/2026-01/graphql.json"

article = {
    "title": "מיניות ואינטימיות בגיל 40+: מה באמת משתנה",
    "excerpt": "שינויים הורמונליים משפיעים על החשק והתשוקה, אבל זה לא סוף הסיפור. איך לשמור על חיבור ותשוקה בשלב הזה של החיים.",
    "body": """<p>מיניות היא חלק בריא וטבעי מהחיים בכל גיל, אבל השינויים ההורמונליים שמתרחשים סביב גיל המעבר יכולים להשפיע על החשק, הריגוש ועל הנוחות הפיזית. חשוב לדעת: זה נורמלי, ויש הרבה מה לעשות.</p>
<h2>מה בעצם משתנה?</h2>
<p>ירידה ברמות האסטרוגן עלולה לגרום ליובש בנרתיק ולירידה באלסטיות הרקמות, מה שהופך חדירה לפחות נעימה עבור חלק מהנשים. גם רמות הטסטוסטרון, שמשפיעות על החשק המיני, נוטות לרדת בהדרגה. לצד זה, עייפות, שינויים במצב הרוח ותחושת דימוי גוף משתנה יכולים להשפיע גם הם.</p>
<h2>מה עוזר בפועל</h2>
<ul>
<li><strong>חומרי סיכה איכותיים:</strong> פותרים חלק ניכר מאי הנוחות הפיזית, ומאפשרים ליהנות שוב בלי כאב.</li>
<li><strong>תקשורת פתוחה עם בן/בת הזוג:</strong> שיחה כנה על מה שמרגיש טוב עכשיו, ולא מה שהיה מרגיש טוב לפני עשר שנים.</li>
<li><strong>זמן איכות ללא לחץ:</strong> להוריד את המשקל מ"ביצועים" ולהתמקד בחיבור, נגיעה וקרבה.</li>
<li><strong>עזרים ומוצרים מותאמים:</strong> ויברטורים ומוצרי הנאה יכולים לעזור לגלות מחדש מה מרגיש טוב עכשיו.</li>
<li><strong>ליווי מקצועי:</strong> אם התחושה של אי נוחות או ירידה בחשק משמעותית, כדאי לשוחח עם רופאה מומחית - יש היום פתרונות טובים, כולל טיפול הורמונלי מקומי.</li>
</ul>
<p>מיניות בגיל 40+ יכולה להיות שונה מבעבר - אבל היא בהחלט יכולה להיות מספקת, מהנה ומלאת חיבור, כשמכירים בשינויים ומתאימים את עצמנו אליהם באהבה.</p>""",
    "author": {"name": "צוות Femit"},
    "isPublished": True,
}

MUTATION = """
mutation articleCreate($article: ArticleCreateInput!) {
  articleCreate(article: $article) {
    article { id title handle }
    userErrors { field message }
  }
}
"""

resp = requests.post(URL, headers={
    "X-Shopify-Access-Token": TOKEN,
    "Content-Type": "application/json"
}, json={"query": MUTATION, "variables": {"article": {
    "blogId": BLOG_ID,
    "title": article["title"],
    "body": article["body"],
    "summary": article["excerpt"],
    "isPublished": True,
    "author": article["author"],
}}})
result = resp.json()
print(json.dumps(result, ensure_ascii=False, indent=2))
