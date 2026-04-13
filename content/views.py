import json

from django.contrib.auth import authenticate
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Page, PageSection, SectionItem, SiteSettings
from .permissions import IsAdminUser, IsSuperAdmin
from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer,
    PageListSerializer, PageDetailSerializer, PageWriteSerializer,
    PageSectionSerializer, PageSectionWriteSerializer,
    SectionItemSerializer, SiteSettingsSerializer,
)


# ── Auth ──────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    ser = LoginSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    user = authenticate(
        username=ser.validated_data['username'],
        password=ser.validated_data['password'],
    )
    if user is None:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    if not user.is_admin_user:
        return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerializer(request.user).data)


# ── Public API ────────────────────────────────────────────────────────

class PageListView(generics.ListAPIView):
    queryset = Page.objects.all()
    serializer_class = PageListSerializer
    permission_classes = [AllowAny]


class PageDetailView(generics.RetrieveAPIView):
    queryset = Page.objects.prefetch_related('sections__items')
    serializer_class = PageDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['lang'] = self.request.query_params.get('lang', 'en')
        return ctx


@api_view(['GET'])
@permission_classes([AllowAny])
def site_settings_view(request):
    settings = SiteSettings.load()
    return Response(SiteSettingsSerializer(settings, context={'request': request}).data)


def _parse_json_field(data, field_name):
    """Parse a JSON string field from request data (handles both JSON and FormData)."""
    value = data.get(field_name)
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}
    return value if value else {}


# ── Admin: Pages ─────────────────────────────────────────────────────

class AdminPageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return PageWriteSerializer
        return PageListSerializer


# ── Admin: Sections ──────────────────────────────────────────────────

class AdminSectionViewSet(viewsets.ModelViewSet):
    queryset = PageSection.objects.select_related('page').prefetch_related('items')
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        qs = super().get_queryset()
        lang = self.request.query_params.get('lang')
        if lang:
            qs = qs.filter(language=lang)
        page_id = self.request.query_params.get('page')
        if page_id:
            qs = qs.filter(page_id=page_id)
        return qs

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return PageSectionWriteSerializer
        return PageSectionSerializer

    def get_serializer_context(self):
        return {**super().get_serializer_context(), 'request': self.request}

    def perform_create(self, serializer):
        settings = _parse_json_field(self.request.data, 'settings')
        lang = self.request.data.get('language', 'en')
        serializer.save(settings=settings, language=lang)

    def perform_update(self, serializer):
        settings = _parse_json_field(self.request.data, 'settings')
        serializer.save(settings=settings)

    @action(detail=True, methods=['patch'], url_path='reorder')
    def reorder(self, request, pk=None):
        section = self.get_object()
        new_order = request.data.get('order')
        if new_order is None:
            return Response({'detail': 'order is required'}, status=400)
        section.order = int(new_order)
        section.save(update_fields=['order'])
        return Response({'status': 'ok', 'order': section.order})


# ── Admin: Items ─────────────────────────────────────────────────────

class AdminItemViewSet(viewsets.ModelViewSet):
    queryset = SectionItem.objects.select_related('section')
    serializer_class = SectionItemSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_context(self):
        return {**super().get_serializer_context(), 'request': self.request}

    def perform_create(self, serializer):
        extra_data = _parse_json_field(self.request.data, 'extra_data')
        serializer.save(extra_data=extra_data)

    def perform_update(self, serializer):
        extra_data = _parse_json_field(self.request.data, 'extra_data')
        serializer.save(extra_data=extra_data)


# ── Admin: Upload ────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def upload_image(request):
    file = request.FILES.get('file')
    if not file:
        return Response({'detail': 'No file provided'}, status=400)

    from django.core.files.storage import default_storage
    path = default_storage.save(f'uploads/{file.name}', file)
    url = request.build_absolute_uri(f'/media/{path}')
    return Response({'url': url, 'path': path})


# ── Admin: Site Settings ─────────────────────────────────────────────

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_site_settings(request):
    settings = SiteSettings.load()
    if request.method == 'PATCH':
        ser = SiteSettingsSerializer(settings, data=request.data, partial=True, context={'request': request})
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)
    return Response(SiteSettingsSerializer(settings, context={'request': request}).data)


# ── Admin: Users (superadmin only) ───────────────────────────────────

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def perform_destroy(self, instance):
        if instance == self.request.user:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Cannot delete yourself')
        instance.delete()
