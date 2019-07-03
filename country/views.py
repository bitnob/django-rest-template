from rest_framework.decorators import list_route
from rest_framework.response import Response
from .models import Country
from .serializers import PublicCountryModelSerializer
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny


class PublicCountryModelViewSet(ReadOnlyModelViewSet):
    """
    List all supported countries to public/authenticated user endpoints
    """
    model = Country
    serializer_class = PublicCountryModelSerializer
    queryset = Country.objects.all()
    permission_classes = [AllowAny]


class AdminCountryModelViewSet(ModelViewSet):
    """
    Admin country management

    """
    model = Country
    serializer_class = PublicCountryModelSerializer
    queryset = Country.objects.all()
    permission_classes = [IsAuthenticated]

    @list_route(methods=['POST'])
    def country_active(self, request):
        """
        change country
        :param request:
        :return:
        """
        country = Country.objects.get(id=request.data['id'])
        country.active = True
        country.save()
        return Response({"success": "Country Successfully Made Active"})

    @list_route(methods=['POST'])
    def country_inactive(self, request):
        """
        change country
        :param request:
        :return:
        """
        country = Country.objects.get(id=request.data['id'])
        country.active = False
        country.save()
        return Response({"success": "Country Successfully Made Inactive"})



