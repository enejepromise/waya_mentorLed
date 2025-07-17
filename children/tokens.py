from rest_framework_simplejwt.tokens import RefreshToken

class ChildRefreshToken(RefreshToken):
    @classmethod
    def for_child(cls, child):
        # Create a bare token without linking to a user
        token = cls()
        token['child_id'] = str(child.id)
        token['child_username'] = child.username
        return token
