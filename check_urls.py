import requests
html = requests.get('https://hypehavenhub.vercel.app/').text
imgs = []
for part in html.split('<img '):
    if 'src="' in part:
        src = part.split('src="')[1].split('"')[0]
        if src.startswith('http'):
            imgs.append(src)

errors = []
for url in imgs:
    if 'r2.dev' in url:
        r = requests.head(url)
        if r.status_code != 200:
            errors.append((url, r.status_code))

print(f'Checked {len(imgs)} images.')
if errors:
    print('Errors found:', errors)
else:
    print('All R2 images returned 200 OK!')
