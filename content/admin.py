from django.contrib import admin
from .models import User, Page, PageSection, SectionItem, SiteSettings


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role',)


class SectionItemInline(admin.TabularInline):
    model = SectionItem
    extra = 0


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'order')


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ('page', 'section_type', 'order', 'title')
    list_filter = ('page', 'section_type')
    inlines = [SectionItemInline]


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    pass
