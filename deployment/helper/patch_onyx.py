import sys
import re

file_path = "/app/onyx/natural_language_processing/search_nlp_models.py"
with open(file_path, "r") as f:
    content = f.read()

# Add log to encode() to see batch size
pattern = r"def encode\(.*?\n( +)if not texts"
replacement = r"""def encode(self, texts, text_type, large_chunks_present=False, local_embedding_batch_size=8, api_embedding_batch_size=10, max_seq_length=512, tenant_id=None, request_id=None):
\1logger.error(f"ENCODE CALLED: api_batch_size={api_embedding_batch_size} provider={self.provider_type}")
\1if not texts"""

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, "w") as f:
    f.write(content)
print("Debug patch applied to encode()")
