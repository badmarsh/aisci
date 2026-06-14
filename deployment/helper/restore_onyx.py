from __future__ import annotations
import sys
import os

file_path = "/app/onyx/natural_language_processing/search_nlp_models.py"
# Restore from backup if exists, or just clean up
# Actually, I will just truncate the file and write a fresh copy from a known clean container?
# No, I will just use sed to remove my specific debug strings.

os.system("sed -i '/LITELLM CALL URL/d' " + file_path)
os.system("sed -i '/LITELLM PROXY CALL/d' " + file_path)
os.system("sed -i '/BATCH SIZE BEING SENT/d' " + file_path)
os.system("sed -i '/EMBED CALL/d' " + file_path)
os.system("sed -i '/ENCODE CALLED/d' " + file_path)
os.system("sed -i '/DEBUG: _make_direct_api_call/d' " + file_path)
os.system("sed -i '/FORCED LITELLM URL/d' " + file_path)

# Special handling for the messed up signatures
# I will just use python to restore the function signatures to original

with open(file_path, "r") as f:
    content = f.read()

import re

# Restore embed signature
pattern = r"async def embed\(self, texts, text_type, model_name=None, deployment_name=None, reduced_dimension=None\):"
replacement = "async def embed(\n        self,\n        *,\n        texts: list[str],\n        text_type: EmbedTextType,\n        model_name: str | None = None,\n        deployment_name: str | None = None,\n        reduced_dimension: int | None = None,\n    ) -> list[Embedding]:"
content = re.sub(pattern, replacement, content)

# Restore encode signature
pattern = r"def encode\(self, texts, text_type, large_chunks_present=False, local_embedding_batch_size=8, api_embedding_batch_size=10, max_seq_length=512, tenant_id=None, request_id=None\):"
replacement = "def encode(\n        self,\n        texts: list[str],\n        text_type: EmbedTextType,\n        large_chunks_present: bool = False,\n        local_embedding_batch_size: int = BATCH_SIZE_ENCODE_CHUNKS,\n        api_embedding_batch_size: int = BATCH_SIZE_ENCODE_CHUNKS_FOR_API_EMBEDDING_SERVICES,\n        max_seq_length: int = DOC_EMBEDDING_CONTEXT_SIZE,\n        tenant_id: str | None = None,\n        request_id: str | None = None,\n    ) -> list[Embedding]:"
content = re.sub(pattern, replacement, content)

# Restore _embed_litellm_proxy signature
# pattern = r"async def _embed_litellm_proxy\(\s+self, texts: list\[str\], model_name: str \| None\s+url = .*?\s+logger.error\(.*?\)\s+if not model_name:"
# This is too hard with regex. I will just do a clean rewrite of the function body.

with open(file_path, "w") as f:
    f.write(content)
print("Restored file signatures")
