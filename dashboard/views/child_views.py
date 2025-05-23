# users/views/child_views.py
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from users.utils import make_pin
from users.permission import IsParentUser
from users.models import Child
from dashboard.serializers import ChildSerializer, ChildCreateSerializer


class ChildViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing child accounts under a parent.
    Supports list, retrieve, create, update, and delete operations.
    Restricted to authenticated parents only.
    """
    permission_classes = [IsAuthenticated, IsParentUser]

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.user)

    def get_serializer_class(self):
        return ChildCreateSerializer if self.action == 'create' else ChildSerializer

    def perform_create(self, serializer):
        serializer.save(parent=self.request.user)

    def retrieve(self, request, pk=None):
        child = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(child)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Allows parent to update child info partially.
        """
        child = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(child, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        Allows parent to delete a child they created.
        """
        child = get_object_or_404(self.get_queryset(), pk=pk)
        child.delete()
        return Response({"message": "Child deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class ParentChangePinView(APIView):
    """
    Allows parent to update a child's PIN securely.
    """
    permission_classes = [IsAuthenticated, IsParentUser]

    def patch(self, request, pk):
        pin = request.data.get('pin')
        if not pin or not pin.isdigit() or len(pin) != 4:
            return Response({"error": "PIN must be exactly 4 digits."}, status=status.HTTP_400_BAD_REQUEST)

        child = get_object_or_404(Child, pk=pk, parent=request.user)
        child.pin = make_pin(pin)
        child.save()
        return Response({"message": "Child PIN updated successfully."})


class ChildAvatarUpdateView(APIView):
    """
    Allows a logged-in child to update their avatar (profile image).
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        try:
            child = Child.objects.get(user=request.user)
        except Child.DoesNotExist:
            return Response({'error': 'Only children can update their avatar.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ChildSerializer(child, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Avatar updated successfully.',
                'avatar': serializer.data.get('avatar')
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChildLoginView(APIView):
    """
    Logs in a child using username and 4-digit PIN.
    Returns access and refresh tokens along with profile info.
    """
    def post(self, request):
        username = request.data.get('username')
        pin = request.data.get('pin')

        if not username or not pin:
            return Response({'error': 'Username and PIN are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            child = Child.objects.get(username=username)
        except Child.DoesNotExist:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

        if not child.check_pin(pin):
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(child)
        return Response({
            'message': 'Login successful.',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'child': {
                'id': str(child.id),
                'username': child.username,
                'avatar': child.avatar.url if child.avatar else None
            }
        }, status=status.HTTP_200_OK)
