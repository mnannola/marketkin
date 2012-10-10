import hmac
import random
import string

SECRET = 'D3lLl@pt0p'

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    return "%s|%s" % (hash_str(name + pw + salt), salt)

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def valid_pw(name, pw, h):
    salt = h.split('|')[1]
    if make_pw_hash(name,pw,salt) == h:
        return True

def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    hsh = hash_str(s)
    return "%s|%s" % (s,hsh)

def valid_secure_val(h):
    values = h.split('|')
    if(make_secure_val(values[0]) == h):
        return True