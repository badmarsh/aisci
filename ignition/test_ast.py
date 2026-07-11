import marko
from marko.ext.gfm import gfm

md = '''
| Claim | Status |
|---|---|
| C1 | Supported |
'''

doc = gfm.parse(md)
for child in doc.children:
    print(child.__class__.__name__)
    if child.__class__.__name__ == 'Table':
        for row in child.children:
            print('Row:', row.__class__.__name__)
            for cell in row.children:
                # cell.children[0] might be RawText
                print(' Cell:', [c.children for c in cell.children])

