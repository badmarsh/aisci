from __future__ import annotations
import sys
with open('/app/onyx/connectors/file/connector.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "import os" in line and "file_name = os.path.basename" in lines[i-1]:
        skip = True
        
    if skip and "continue" in line:
        skip = False
        continue
        
    if not skip:
        new_lines.append(line)

# Also fix the duplicate if str(file_id).startswith("/workspace/")!
# Let's just do a simpler fix:
# Read the file as a string.
with open('/app/onyx/connectors/file/connector.py', 'r') as f:
    text = f.read()

import re
# Remove the bad block
text = re.sub(r'            if str\(file_id\)\.startswith\("/workspace/"\) and os\.path\.exists\(file_id\):\n                file_name = os\.path\.basename\(file_id\)\n                import os.*?                continue\n', '', text, flags=re.DOTALL)

with open('/app/onyx/connectors/file/connector.py', 'w') as f:
    f.write(text)
print("Fixed connector.py")
