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
    serializer_class = ChildUpdateSerializer
    permission_classes = [IsAuthenticated, IsParentOfChild]
    queryset = Child.objects.all()


class ChildDeleteView(generics.DestroyAPIView):
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

        if child.check_pin(pin):
            refresh = RefreshToken.for_user(child.parent)
            return Response({
                'childId': str(child.id),
                'childUsername': child.username,
                'parentId': str(child.parent.id),
                'token': str(refresh.access_token),
                'refresh': str(refresh),
            })

        return Response(
            {"detail": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )
