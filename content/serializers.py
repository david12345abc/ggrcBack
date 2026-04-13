from rest_framework import serializers
from .models import User, Page, PageSection, SectionItem, SiteSettings


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'is_active')
        read_only_fields = ('id',)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class SectionItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SectionItem
        fields = (
            'id', 'section', 'order', 'title', 'description',
            'image', 'image_url', 'icon_name',
            'link_url', 'link_text', 'extra_data',
        )
        read_only_fields = ('id',)

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class PageSectionSerializer(serializers.ModelSerializer):
    items = SectionItemSerializer(many=True, read_only=True)
    background_image_url = serializers.SerializerMethodField()

    class Meta:
        model = PageSection
        fields = (
            'id', 'page', 'section_type', 'language', 'order', 'title', 'subtitle',
            'background_image', 'background_image_url', 'settings', 'items',
        )
        read_only_fields = ('id',)

    def get_background_image_url(self, obj):
        if obj.background_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.background_image.url)
            return obj.background_image.url
        return None


class PageSectionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageSection
        fields = (
            'id', 'page', 'section_type', 'language', 'order', 'title', 'subtitle',
            'background_image', 'settings',
        )
        read_only_fields = ('id',)


class PageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'slug', 'title', 'order', 'show_in_nav')


class PageWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'slug', 'title', 'meta_description', 'order', 'show_in_nav')
        read_only_fields = ('id',)


class PageDetailSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ('id', 'slug', 'title', 'meta_description', 'order', 'show_in_nav', 'sections')

    def get_sections(self, obj):
        lang = self.context.get('lang', 'en')
        qs = obj.sections.filter(language=lang).order_by('order')
        return PageSectionSerializer(qs, many=True, context=self.context).data


class SiteSettingsSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    logo_purple_url = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = (
            'id', 'address', 'address_short', 'phones', 'phone_display',
            'email', 'instagram_url', 'linkedin_url', 'facebook_url',
            'youtube_video_id', 'logo', 'logo_url', 'logo_purple', 'logo_purple_url',
        )

    def _build_url(self, image_field):
        if image_field:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image_field.url)
            return image_field.url
        return None

    def get_logo_url(self, obj):
        return self._build_url(obj.logo)

    def get_logo_purple_url(self, obj):
        return self._build_url(obj.logo_purple)
