from .. import DB, commit
from ..helpers import fernet_encrypted, fernet_decrypted
from cryptography.fernet import InvalidToken
import string, random, pyotp


class UserSettings:

    # Security Section
    twofa_enabled = DB.Column(DB.Boolean, default=False)
    twofa_secret_enc = DB.Column(DB.String(172))
    twofa_recovery = DB.Column(DB.String(53))
    login_notify = DB.Column(DB.Boolean, default=True)

    def enable_2fa(self, secret: str) -> list[str]:
        codes = [''.join(random.choices(string.digits, k=8)) for _ in range(6)]

        self.twofa_enabled = True
        self.twofa_secret_enc = fernet_encrypted(secret.encode())
        self.twofa_recovery = '|'.join(codes)

        return codes

    def check_2fa_token(self, token: str) -> bool:
        if len(token) == 8 and self.twofa_recovery:
            codes = self.twofa_recovery.split('|')
            if token in codes:
                codes.remove(token)
                self.twofa_recovery = '|'.join(codes)
                commit()
                return True
            return False

        try:
            if not self.twofa_secret_enc:
                return False
            secret = fernet_decrypted(self.twofa_secret_enc.encode())
            return pyotp.TOTP(secret).verify(token)
        except (TypeError, AttributeError, InvalidToken):
            return False

    def disable_2fa(self):
        self.twofa_enabled = False
        self.twofa_secret_enc = None
        self.twofa_recovery = None


    # Privacy Section
    # TODO: Not implemented yet


    # Account Section
    # TODO: Not implemented yet


    # Newsletter Section
    # TODO: Not implemented yet
