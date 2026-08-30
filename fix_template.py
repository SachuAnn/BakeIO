import re

file_path = r'd:\BAKEIO\templates\products\cake_detail.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix split username
content = content.replace('{{\n                                    review.user.username }}', '{{ review.user.username }}')

# Fix split rating if
content = content.replace('{% if forloop.counter <=\n                                        review.rating %}', '{% if forloop.counter <= review.rating %}')

# Fix split comment
content = content.replace('{{\n                                review.comment }}', '{{ review.comment }}')

# Fix split date
content = content.replace('{{ review.created_at|date:"M d,\n                                Y" }}', '{{ review.created_at|date:"M d, Y" }}')

# Also handle potential multiple spaces/newlines
content = re.sub(r'\{\{\s+review\.user\.username\s+\}\}', '{{ review.user.username }}', content)
content = re.sub(r'\{%\s+if\s+forloop\.counter\s+<=\s+review\.rating\s+%\}', '{% if forloop.counter <= review.rating %}', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fix applied successfully")
