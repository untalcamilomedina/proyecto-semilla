from app.core.security import get_password_hash

password = "admin123"
hashed_password = get_password_hash(password)
print(hashed_password)