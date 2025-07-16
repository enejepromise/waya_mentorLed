from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

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
        # Assign the logged-in user as the parent
        serializer.save(parent=self.request.user)


class ChildListView(generics.ListAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only children belonging to the logged-in parent
        return Child.objects.filter(parent=self.request.user)


class ChildDetailView(generics.RetrieveAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated, IsParentOfChild]
    queryset = Child.objects.all()


class ChildUpdateView(generics.UpdateAPIView):
    """
    PUT /api/kids/{id}/ - Update a child's account
    """
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
            return Response(
                {"detail": "Server error: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
        refresh = RefreshToken()
        refresh['child_id'] = str(child.id)
        refresh['child_username'] = child.username
        # Add any additional custom claims as needed here

        access_token = refresh.access_token

        return Response({
            'childId': str(child.id),
            'childUsername': child.username,
            'token': str(access_token),
            'refresh': str(refresh),
        })
