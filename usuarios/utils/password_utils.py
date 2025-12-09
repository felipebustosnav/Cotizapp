import secrets
import string

def generar_password_temporal(longitud=10):
    """
    Genera una contraseña temporal segura.
    Debe contener al menos:
    - 1 letra mayúscula
    - 1 letra minúscula
    - 1 dígito
    - 1 caracter especial
    """
    alfabeto = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alfabeto) for i in range(longitud))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*" for c in password)):
            return password
