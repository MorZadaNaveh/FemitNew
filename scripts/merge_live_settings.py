import json, re

def load_stripped(path):
    text = open(path).read()
    text = re.sub(r'^/\*.*?\*/', '', text, flags=re.S)
    return json.loads(text)

dev = load_stripped('theme/config/settings_data.json')
live = load_stripped('live-theme/config/settings_data.json')

dev_settings = dev['presets']['Dawn']
live_current = live['current']

# Brand-defining keys we intentionally set for Femit — everything else in the
# live store's real settings (social links, favicon, cart config, etc.) stays untouched.
brand_keys = [
    'type_header_font', 'type_body_font',
    'buttons_radius', 'buttons_border_thickness',
    'inputs_radius',
    'card_corner_radius', 'card_text_alignment', 'card_shadow_opacity', 'card_shadow_blur', 'card_color_scheme',
    'collection_card_corner_radius', 'collection_card_text_alignment', 'collection_card_shadow_opacity', 'collection_card_shadow_blur', 'collection_card_color_scheme',
    'blog_card_corner_radius', 'blog_card_text_alignment', 'blog_card_shadow_opacity', 'blog_card_shadow_blur', 'blog_card_color_scheme',
    'popup_corner_radius', 'media_radius',
]

for key in brand_keys:
    if key in dev_settings:
        live_current[key] = dev_settings[key]

# Color schemes: overlay scheme-1 and scheme-2 (the ones our sections/global styles use)
# preserving any other schemes (scheme-3, scheme-4, etc.) the live store already has.
if 'color_schemes' not in live_current:
    live_current['color_schemes'] = {}
for scheme_id in ['scheme-1', 'scheme-2']:
    if scheme_id in dev_settings.get('color_schemes', {}):
        live_current['color_schemes'][scheme_id] = dev_settings['color_schemes'][scheme_id]

live['current'] = live_current

with open('live-theme-merged/config/settings_data.json', 'w') as f:
    json.dump(live, f, indent=2, ensure_ascii=False)

print("Merged settings_data.json written.")
print("Brand keys applied:", brand_keys)
