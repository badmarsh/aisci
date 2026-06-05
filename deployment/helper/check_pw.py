import sys
import bcrypt
import base64
import hashlib

h = "$2b$12$3VvxFvy1goxWtYbKQwFawublLzmkfyulbmlUt.UiAfRJhtIoTop.y"
pws = ['admin', 'admin1234', 'Admin1234!', 'deerflow', 'password']

pre = lambda p: base64.b64encode(hashlib.sha256(p.encode()).digest())
for pw in pws:
    try:
        match = bcrypt.checkpw(pre(pw), h.encode())
        print(f"{pw}: {match}")
    except Exception as e:
        print(f"Error {pw}: {e}")
