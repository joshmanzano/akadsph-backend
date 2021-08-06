from django.contrib.auth.models import User, Group
from rest_framework import viewsets 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from core.serializers import UserSerializer, GroupSerializer
from django.conf import settings

@api_view(['GET'])
def database_check(request):
    if request.method == 'GET':
        engine = settings.DATABASES['default']['ENGINE']
        host = settings.DATABASES['default']['HOST']
        return Response({
            'ENGINE': engine,
            'HOST': host
        })

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]