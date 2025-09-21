from os import getenv

def check_password(password: str) -> bool: 
    if password != getenv("UPDATE_PASSWORD"): raise ValueError("Password is incorrect")
    return True