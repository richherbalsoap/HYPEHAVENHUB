with open('store/admin_views.py', 'r') as f:
    content = f.read()
content = content.replace('"\\""', '"""')
with open('store/admin_views.py', 'w') as f:
    f.write(content)
