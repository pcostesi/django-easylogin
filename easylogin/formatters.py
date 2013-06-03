import hashlib

def nine_numbers(user, salt, timestamp):
    user_hash = hashlib.sha256(salt)
    user_hash.update(timestamp)
    user_hash.update(str(user.id))
    user_hash.update(user.username)
    number = int(user_hash.hexdigest(), 16)
    return str(number % (10 ** 9))


def short_hex(user, salt, timestamp):
    user_hash = hashlib.sha256(salt)
    user_hash.update(timestamp)
    user_hash.update(str(user.id))
    user_hash.update(user.username)
    return user_hash.hexdigest()[:8]