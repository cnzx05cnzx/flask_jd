import re

tar = 'https://itemjd.com/1000303952.html'

pattern = re.compile('^https://item.jd.com/[0-9]+.html$')
if pattern.search(tar):
    print('yes')
else:
    print('no')
# print(pattern.search(tar))
