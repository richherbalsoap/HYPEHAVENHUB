import re

with open('.env.production', 'r') as f:
    content = f.read()

content = re.sub(r'DEBUG="(.*?)"', r'DEBUG=\1', content)
content = re.sub(r'DATABASE_URL="(.*?)"', r'DATABASE_URL=\1', content)
content = re.sub(r'POSTGRES_URL="(.*?)"', r'POSTGRES_URL=\1', content)

with open('.env.production', 'w') as f:
    f.write(content)

print("Fixed quotes in .env.production")
