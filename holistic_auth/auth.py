from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from knox.auth import TokenAuthentication as KnoxTokenAuthentication
from rest_framework.authentication import BasicAuthentication as DRFBasicAuthentication
from rest_framework.exceptions import AuthenticationFailed


User = get_user_model()


class BasicAuthentication(DRFBasicAuthentication):

    def authenticate_credentials(self, userid, password, request=None):
        """
        We override this method to silently ignore
        validation checks for inactive user (`User.is_active=False`).

        TODO:
        If User's account activation through their email address is required,
        we can use the `DRFBasicAuthentication` directly.
        """
        user = authenticate(request=request, username=userid, password=password)

        if not user:
            raise AuthenticationFailed(_('Invalid username/password.'))

        return (user, None)


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
