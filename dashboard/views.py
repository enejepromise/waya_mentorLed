from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Child
from .serializers import ChildSerializer, ChildCreateSerializer

# Create your views here.
class ChildListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChildCreateSerializer
        return ChildSerializer

    def perform_create(self, serializer):
        serializer.save()
