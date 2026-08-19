from app.core.security import hash_password, verify_password

password = "admin123"

hashed = hash_password(password)

print("Password:", password)
print("Hashed :", hashed)

print("Verify:", verify_password(password, hashed))

