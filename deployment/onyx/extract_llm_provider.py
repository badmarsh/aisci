import sys

in_table = False
with open('db_dump.sql', 'r', encoding='utf-8') as f:
    with open('llm_provider_dump_wsl.txt', 'w', encoding='utf-8') as out:
        for line in f:
            if line.startswith('COPY public.llm_provider '):
                in_table = True
                out.write(line)
                continue
            if in_table:
                if line.startswith('\\.'):
                    break
                out.write(line)
