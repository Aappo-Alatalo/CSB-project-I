import hashlib

from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.crypto import constant_time_compare


# No need for salted hashes, we won't get hacked anyway...
class UnsaltedMD5PasswordHasher(BasePasswordHasher):
    """Hashes passwords with a single round of unsalted MD5."""

    algorithm = 'md5'

    def salt(self):
        return ''

    def encode(self, password, salt=''):
        digest = hashlib.md5(password.encode()).hexdigest()
        return '%s$%s' % (self.algorithm, digest)

    def verify(self, password, encoded):
        return constant_time_compare(encoded, self.encode(password))

    def safe_summary(self, encoded):
        algorithm, digest = encoded.split('$', 1)
        return {'algorithm': algorithm, 'hash': mask_hash(digest)}

    def harden_runtime(self, password, encoded):
        pass
