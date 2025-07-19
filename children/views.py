from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from children.authentication import ChildJWTAuthentication
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

    # Implements caching and restricts retrieved fields for efficiency
    def get_queryset(self):
        parent = self.request.user
        cache_key = f"children_list_{parent.id}"
        queryset = cache.get(cache_key)
        if queryset is not None:
            return queryset
        # Only retrieve commonly used fields for performance
        queryset = Child.objects.filter(parent=parent).only('id', 'username', 'name', 'avatar')
        cache.set(cache_key, queryset, timeout=60 * 5)
        return queryset


class ChildDetailView(generics.RetrieveAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated, IsParentOfChild]
    queryset = Child.objects.all()

    def get_object(self):
        child = self.request.user.child  # Assuming child user is logged in
        cache_key = f"child_detail_{child.id}"
        cached_child = cache.get(cache_key)
        if cached_child is not None:
            return cached_child
        cache.set(cache_key, child, timeout=60 * 5)
        return child


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


class ChildLoginView(generics.GenericAPIView):
    serializer_class = ChildLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        pin = serializer.validated_data['pin']

        try:
            child = Child.objects.only('id', 'username', 'name', 'avatar', 'pin').get(username=username)
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


class ChildSelfDetailView(generics.RetrieveAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [ChildJWTAuthentication]

    def get_object(self):
        return self.request.user  # or request.child if you set both
