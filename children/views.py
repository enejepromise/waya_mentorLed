# children/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from children.authentication import ChildJWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from children.tokens import ChildRefreshToken

from .models import Child
from .serializers import (
    ChildCreateSerializer,
    ChildSerializer,
    ChildUpdateSerializer,
    ChildLoginSerializer
)
from .permissions import IsParentOfChild


class ChildCreateView(generics.CreateAPIView):
    serializer_class = ChildCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(parent=self.request.user)


class ChildListView(generics.ListAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.user)


class ChildDetailView(generics.RetrieveAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated, IsParentOfChild]
    queryset = Child.objects.all()


class ChildUpdateView(generics.UpdateAPIView):
    serializer_class = ChildUpdateSerializer
    permission_classes = [IsAuthenticated, IsParentOfChild]
    queryset = Child.objects.all()

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Child.DoesNotExist:
            return Response({"detail": "Child not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChildDeleteView(generics.DestroyAPIView):
    serializer_class = ChildSerializer  
    permission_classes = [IsAuthenticated, IsParentOfChild]
    queryset = Child.objects.all()

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            return Response({"detail": "Server error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from .permissions import IsParentOfChild


class ChildLoginView(generics.GenericAPIView):
    serializer_class = ChildLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        pin = serializer.validated_data['pin']

        try:
            child = Child.objects.get(username=username)
        except Child.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not child.check_pin(pin):
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Create child-specific JWT tokens manually
        refresh = ChildRefreshToken.for_child(child)
        access_token = refresh.access_token

        return Response({
            "id": str(child.id),
            "name": child.name,
            "username": child.username,
            "avatar": request.build_absolute_uri(child.avatar.url) if child.avatar else None,
            "token": str(access_token),
            "refresh": str(refresh),
        })




# Example child-protected view using custom auth
class ChildSelfDetailView(generics.RetrieveAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [ChildJWTAuthentication]

    def get_object(self):
        return self.request.user  # or request.child if you set both
