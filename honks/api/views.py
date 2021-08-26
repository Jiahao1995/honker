from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from honks.api.serializers import HonkCreateSerializer, HonkSerializer
from honks.models import Honk
from newsfeeds.services import NewsFeedService


class HonkViewSet(viewsets.GenericViewSet,
                  viewsets.mixins.CreateModelMixin,
                  viewsets.mixins.ListModelMixin):
    """
    API endpoint that allows users to create, list honks
    """
    queryset = Honk.objects.all()
    serializer_class = HonkCreateSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """
        reload create() method
        """
        serializer = HonkCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=400)
        honk = serializer.save()
        NewsFeedService.fan_out_to_followers(honk)
        return Response(HonkSerializer(honk).data, status=201)

    def list(self, request, *args, **kwargs):
        """
        reload list() method
        """
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)

        honks = Honk.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        serializer = HonkSerializer(honks, many=True)
        return Response({'honks': serializer.data})
