import pyotp

def generate_totp():
    SECRET = "5ZYAACBBYFATZ4QOIE6CMV5VUA"  # the string you got in Step 1
    totp = pyotp.TOTP(SECRET)
    returned_totp = totp.now()
    print("Current TOTP:", totp.now())
    return returned_totp