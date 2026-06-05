import json
with open('llm_provider_dump_wsl.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith('5\tLiteLLM\t'):
            parts = line.split('\t')
            # the schema is: id, name, default_model_name, provider, fast_default_model_name, model_configurations, is_public, display_model_name
            # index 5 is model_configurations
            try:
                # Need to unescape \\ in the TSV format
                raw_json = parts[5]
                # In PostgreSQL COPY output, backslashes are escaped.
                # However, json might contain double escapes depending on how it was dumped.
                # Let's try replacing \\n, \\", etc. if necessary.
                
                raw_json = raw_json.replace('\\\\', '\\')
                
                configs = json.loads(raw_json)
                for c in configs:
                    if 'qwen-fast' in c.get('name', ''):
                        print("==== FOUND qwen-fast ====")
                        print(json.dumps(c, indent=2))
                    if 'gemini' in str(c).lower():
                        print("==== FOUND gemini in model ====")
                        print(json.dumps(c, indent=2))
            except Exception as e:
                print(f"Error parsing json: {e}")
            break
