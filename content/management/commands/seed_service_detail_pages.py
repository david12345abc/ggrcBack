# -*- coding: utf-8 -*-
"""
Create Your Pages (show_in_nav=False) for each service card, link cards on /services,
and seed hero + HTML text content. Run after seed_services_page.
"""
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from content.models import Page, PageSection, SectionItem
from content.management.commands.seed_services_page import SERVICES_ROWS, SEED_DIR
from content.service_detail_bodies import DETAIL_SLUGS, SERVICE_BODIES_EN

LANGUAGES = ('en', 'ru', 'am')


class Command(BaseCommand):
    help = 'Create service detail pages under Your Pages and link Services cards to /page/<slug>.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Recreate detail page sections (hero + text) if they already exist.',
        )
        parser.add_argument(
            '--skip-links',
            action='store_true',
            help='Do not update link_url on Services page cards.',
        )

    def handle(self, *args, **options):
        replace = options['replace']
        skip_links = options['skip_links']

        if len(DETAIL_SLUGS) != len(SERVICES_ROWS):
            self.stderr.write(self.style.ERROR('DETAIL_SLUGS and SERVICES_ROWS length mismatch.'))
            return

        rows = list(zip(DETAIL_SLUGS, SERVICES_ROWS))

        for slug, (filename, card_title, _card_desc) in rows:
            short_title = card_title[:80] + ('…' if len(card_title) > 80 else '')
            page, _ = Page.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': short_title,
                    'show_in_nav': False,
                    'order': 100,
                    'meta_description': f'{card_title} — GGRC Armenia.',
                },
            )

            for lang in LANGUAGES:
                existing = PageSection.objects.filter(page=page, language=lang).exists()
                if existing and not replace:
                    continue

                PageSection.objects.filter(page=page, language=lang).delete()

                hero = PageSection.objects.create(
                    page=page,
                    language=lang,
                    section_type='hero',
                    order=1,
                    title=card_title,
                    subtitle='',
                    settings={
                        'service_detail_hero': True,
                        'service_breadcrumb': True,
                        'text_color': '#ffffff',
                        'font_weight': '800',
                    },
                )
                src = SEED_DIR / filename
                if not src.is_file():
                    self.stderr.write(self.style.WARNING(f'Missing seed image: {src}'))
                else:
                    item = SectionItem.objects.create(
                        section=hero,
                        order=0,
                        title='',
                        description='',
                    )
                    with open(src, 'rb') as f:
                        item.image.save(f'services/pages/{slug}/{filename}', File(f), save=True)

                body = SERVICE_BODIES_EN.get(slug, '<p>Content coming soon.</p>')
                PageSection.objects.create(
                    page=page,
                    language=lang,
                    section_type='text_block',
                    order=2,
                    title='',
                    subtitle='',
                    settings={
                        'body': body.strip(),
                        'body_format': 'html',
                    },
                )

            self.stdout.write(self.style.SUCCESS(f'  Page /page/{slug}/ ({card_title[:40]}...)'))

        if not skip_links:
            services_page = Page.objects.filter(slug='services').first()
            if not services_page:
                self.stderr.write(self.style.WARNING('Services page not found; run seed_services_page first.'))
            else:
                for lang in LANGUAGES:
                    sec = PageSection.objects.filter(
                        page=services_page,
                        language=lang,
                        section_type='services',
                    ).first()
                    if not sec:
                        continue
                    items = list(sec.items.order_by('order'))
                    for idx, slug in enumerate(DETAIL_SLUGS):
                        if idx >= len(items):
                            break
                        items[idx].link_url = f'/page/{slug}'
                        items[idx].link_text = ''
                        items[idx].save(update_fields=['link_url', 'link_text'])
                self.stdout.write(self.style.SUCCESS('  Linked Services cards to detail pages.'))

        self.stdout.write(self.style.SUCCESS('Service detail pages finished.'))
