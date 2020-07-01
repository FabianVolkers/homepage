from django.contrib.auth.tokens import PasswordResetTokenGenerator


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, contact, timestamp):
        return (
            str(contact.pk) + str(timestamp) +
            str(contact.email_address)
        )

account_activation_token = TokenGenerator()