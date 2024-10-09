from rest_framework import authentication
from rest_framework import exceptions

class CustomAuthentication(authentication.TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')
        
        if not token.user.is_verified:
            raise exceptions.AuthenticationFailed('Email not verified.')

        return (token.user, token)