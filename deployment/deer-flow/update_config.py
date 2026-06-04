import yaml

with open('config.example.yaml', 'r') as f:
    ex = f.readlines()
with open('config.yaml', 'r') as f:
    lv = f.readlines()

s_ex = next(i for i,l in enumerate(ex) if l.startswith('models:'))
e_ex = next(i for i,l in enumerate(ex) if l.startswith('tool_groups:'))

s_lv = next(i for i,l in enumerate(lv) if l.startswith('models:'))
e_lv = next(i for i,l in enumerate(lv) if l.startswith('tool_groups:'))

new_lv = lv[:s_lv] + ex[s_ex:e_ex] + lv[e_lv:]
with open('config.yaml', 'w') as f:
    f.writelines(new_lv)

print('Config updated!')
