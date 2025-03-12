import base64
import hashlib
import secrets

ALGORITHM = "pbkdf2_sha256"


def hash_password(password, salt=None, iterations=260000):
    if salt is None:
        salt = secrets.token_hex(16)
    assert salt and isinstance(salt, str) and "$" not in salt
    assert isinstance(password, str)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    b64_hash = base64.b64encode(pw_hash).decode("ascii").strip()
    return "{}${}${}${}".format(ALGORITHM, iterations, salt, b64_hash)


def verify_password(password, password_hash):
    if (password_hash or "").count("$") != 3:
        return False
    algorithm, iterations, salt, b64_hash = password_hash.split("$", 3)
    iterations = int(iterations)
    assert algorithm == ALGORITHM
    compare_hash = hash_password(password, salt, iterations)
    return secrets.compare_digest(password_hash, compare_hash)



""" clave='hola'
print(hash_password(clave,'sena2025',600000))
print(hash_password(clave)) # ! Se puede omitir la salt para que el hash sea cambiante , se pone la salt automatica es mejor esta opcion
hash = 'pbkdf2_sha256$600000$sena2025$n6uiSQK6eftdb/FhC8BKhL6g4vh+e1Hen+HhbOTD/3Y='
hash2='pbkdf2_sha256$260000$4e3c3baae659b285921b584cdef2599d$n4NT4vXUNvpyQBlSDd9IewkQeJG6tRmLsA3raUN6a9I='
print(verify_password(clave,hash))
print(verify_password(clave,hash2)) """