from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('admin', 'Administrator'),
        ('superadmin', 'Super Administrator'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')

    class Meta:
        db_table = 'users'

    @property
    def is_admin_user(self):
        return self.role in ('admin', 'superadmin')

    @property
    def is_superadmin(self):
        return self.role == 'superadmin'


class Page(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    meta_description = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'pages'
        ordering = ['order']

    def __str__(self):
        return self.title


LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('ru', 'Русский'),
    ('am', 'Հայերեն'),
]


class PageSection(models.Model):
    SECTION_TYPES = [
        ('hero', 'Hero'),
        ('features_carousel', 'Features Carousel'),
        ('about_teaser', 'About Teaser'),
        ('services', 'Services'),
        ('why_choose_us', 'Why Choose Us'),
        ('team', 'Team'),
        ('steps', 'Steps'),
        ('testimonials', 'Testimonials'),
        ('blog', 'Blog'),
        ('about_hero_text', 'About Hero Text'),
        ('about_values', 'About Values'),
        ('about_tech', 'About Tech'),
        ('about_video', 'About Video'),
        ('about_conference', 'About Conference'),
        ('text_block', 'Text Block'),
        ('card_grid', 'Card Grid'),
        ('card_carousel', 'Card Carousel'),
    ]

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=30, choices=SECTION_TYPES)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=300, blank=True, default='')
    subtitle = models.TextField(blank=True, default='')
    background_image = models.ImageField(upload_to='sections/', blank=True, null=True)
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'page_sections'
        ordering = ['page', 'order']

    def __str__(self):
        return f'{self.page.slug} — {self.section_type} #{self.order}'


class SectionItem(models.Model):
    section = models.ForeignKey(PageSection, on_delete=models.CASCADE, related_name='items')
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=300, blank=True, default='')
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    icon_name = models.CharField(max_length=50, blank=True, default='')
    link_url = models.URLField(max_length=500, blank=True, default='')
    link_text = models.CharField(max_length=100, blank=True, default='')
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'section_items'
        ordering = ['section', 'order']

    def __str__(self):
        return f'{self.section} — item #{self.order}'


class SiteSettings(models.Model):
    address = models.CharField(max_length=300, blank=True, default='')
    address_short = models.CharField(max_length=200, blank=True, default='')
    phones = models.JSONField(default=list, blank=True)
    phone_display = models.CharField(max_length=200, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    instagram_url = models.URLField(blank=True, default='')
    linkedin_url = models.URLField(blank=True, default='')
    facebook_url = models.URLField(blank=True, default='')
    youtube_video_id = models.CharField(max_length=50, blank=True, default='')
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    logo_purple = models.ImageField(upload_to='site/', blank=True, null=True)

    class Meta:
        db_table = 'site_settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
