import os

env_path = "/home/ubuntu/aisci/deployment/onyx/.env"
with open(env_path, "a") as f:
    f.write("\nGEN_AI_MAX_TOKENS=128000\n")
    f.write("FAST_GEN_AI_MAX_TOKENS=128000\n")

print("Appended token limits to .env")
