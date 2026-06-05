with open("/tmp/index_settings.js", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer("multipass_indexing", content)]
print(f"Found {len(matches)} occurrences:")
for i, start in enumerate(matches):
    print(f"Occurrence {i+1}:")
    print(content[max(0, start - 600): min(len(content), start + 600)])
    print("-" * 50)
