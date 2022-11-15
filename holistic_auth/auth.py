from knox.auth import TokenAuthentication as KnoxTokenAuthentication


class TokenAuthentication(KnoxTokenAuthentication):

    def validate_user(self, auth_token):
        """
        We override this method to silently ignore
        validation checks for inactive user (`User.is_active=False`).

        TODO:
        If User's account activation through their email address is required,
        we can use the `KnoxTokenAuthentication` directly.
        """
        return (auth_token.user, auth_token)
