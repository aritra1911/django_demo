from rest_framework import viewsets, mixins, authentication, parsers, renderers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from demoapp.models import Customer
from demoapp.serializers import AuthEmailTokenSerializer, CustomerSerializer
from demoapp.permissions import IsCustomerAuthenticated


class ObtainAuthTokenWithEmail(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )

    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = AuthEmailTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({'token': token.key})


class CustomerViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsCustomerAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(id=self.request.user.id)
        return queryset
