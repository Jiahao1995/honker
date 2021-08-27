from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from honks.api.serializers import HonkCreateSerializer, HonkSerializer, HonkSerializerWithComments
from honks.models import Honk
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params


class HonkViewSet(viewsets.GenericViewSet,
                  viewsets.mixins.CreateModelMixin,
                  viewsets.mixins.ListModelMixin):
    """
    API endpoint that allows users to create, list honks
    """
    queryset = Honk.objects.all()
    serializer_class = HonkCreateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        honk = self.get_object()
        return Response(HonkSerializerWithComments(honk).data)

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

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        honks = Honk.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        serializer = HonkSerializer(honks, many=True)
        return Response({'honks': serializer.data})
