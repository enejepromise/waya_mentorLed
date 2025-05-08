from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from ..models.user import User
from ..models.child import Child
from ..serializers.user import RegisterSerializer, LoginSerializer
from ..serializers.child import CreateChildSerializer

class RegisterView(APIView):
    """
    POST /api/register/
    Registers a new parent user.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': str(user.id),
                    'fullname': user.fullname,
                    'email': user.email,
                    'role': 'parent',
                    'family_id': str(user.id),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    POST /api/login/
    Authenticates a user (parent or child) and returns JWT tokens.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        role = request.data.get('role')

        if role == 'parent':
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': str(user.id),
                        'fullname': user.fullname,
                        'email': user.email,
                        'role': 'parent',
                        'family_id': str(user.id),
                    }
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif role == 'child':
            username = request.data.get('username')
            password = request.data.get('password')

            try:
                child = Child.objects.get(username=username)
            except Child.DoesNotExist:
                return Response({'error': 'Child not found'}, status=status.HTTP_404_NOT_FOUND)

            if not child.check_password(password):
                return Response({'error': 'Invalid child password'}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken()
            refresh['child_id'] = str(child.id)
            refresh['role'] = 'child'
            refresh['family_id'] = str(child.parent.id)

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': str(child.id),
                    'fullname': child.fullname,
                    'username': child.username,
                    'role': 'child',
                    'family_id': str(child.parent.id),
                }
            })

        return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
