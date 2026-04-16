# -*- coding: utf-8 -*-
"""Populate the /services page with service cards and images from seed_assets."""
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from content.models import Page, PageSection, SectionItem

SEED_DIR = Path(__file__).resolve().parent.parent.parent / 'seed_assets' / 'services'

# (image filename, title, description) — optional description under title
SERVICES_ROWS = [
    ('01-infertility-diagnosis.png', 'INFERTILITY DIAGNOSIS AND TREATMENT', '(FOR WOMEN AND MEN)'),
    ('02-ivf-icsi.png', 'IN VITRO FERTILIZATION (IVF/ICSI)', ''),
    ('03-surrogacy-donation.png', 'SURROGACY AND DONATION', ''),
    ('04-ambulatory-gynecology.png', 'AMBULATORY GYNECOLOGY', ''),
    ('05-hormonal-genetic-testing.jpg', 'HORMONAL AND GENETIC TESTING', ''),
    (
        '06-infections-hormonal-disorders.jpg',
        'DIAGNOSIS OF INFECTIONS, HORMONAL IMBALANCE, AND RELATED DISORDERS',
        '',
    ),
    ('07-advanced-lab-embryology.png', 'ADVANCED LABORATORY AND EMBRYOLOGICAL TECHNOLOGIES', ''),
    ('08-pregnancy-planning.png', 'PREGNANCY PLANNING AND MONITORING', ''),
    ('09-medical-consultation.png', 'MEDICAL CONSULTATION', ''),
    ('10-financial-support-couples.png', 'FINANCIAL SUPPORT PROGRAMS FOR COUPLES', ''),
    ('11-oncology-reproductive.png', 'REPRODUCTIVE SERVICES FOR ONCOLOGY PATIENTS', ''),
]

SECTION_I18N = {
    'en': {
        'title': 'OUR SERVICES',
        'subtitle': 'GGRC Armenia offers a wide range of services, including',
    },
    'ru': {
        'title': 'НАШИ УСЛУГИ',
        'subtitle': 'GGRC Armenia предлагает широкий спектр услуг, включая',
    },
    'am': {
        'title': (
            '\u0544\u0535\u054c \u053e\u0531\u054c\u0531\u0545\u0548\u0552\u0539\u0545\u0548\u0552\u0546\u0546\u0535\u054c\u0538'
        ),
        'subtitle': (
            'GGRC Armenia-\u0576 \u0561\u057c\u0561\u057b\u0561\u0580\u056f\u043e\u0582\u043c \u0567 '
            '\u056e\u0561\u057c\u0561\u0575\u043e\u0582\u0569\u0575\u043e\u0582\u0576\u0576\u0565\u0580\u056b '
            '\u043b\u0561\u0575\u0576 \u0577\u0580\u057b\u0561\u0576\u0561\u056f, \u0576\u0565\u0580\u0561\u057c\u0575\u0561\u043b'
        ),
    },
}


class Command(BaseCommand):
    help = 'Create / update Services page sections and 11 service cards (content/seed_assets/services/).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Remove existing service items on the Services page and re-import.',
        )

    def handle(self, *args, **options):
        replace = options['replace']
        if not SEED_DIR.is_dir():
            self.stderr.write(self.style.ERROR(f'Missing seed folder: {SEED_DIR}'))
            return

        page, _ = Page.objects.update_or_create(
            slug='services',
            defaults={
                'title': 'Services',
                'order': 2,
                'show_in_nav': True,
                'meta_description': 'GGRC Armenia medical and reproductive services.',
            },
        )

        for lang, labels in SECTION_I18N.items():
            section, created = PageSection.objects.get_or_create(
                page=page,
                language=lang,
                section_type='services',
                defaults={
                    'order': 1,
                    'title': labels['title'],
                    'subtitle': labels['subtitle'],
                    'settings': {'css_class': 'services'},
                },
            )
            if not created:
                section.title = labels['title']
                section.subtitle = labels['subtitle']
                section.order = 1
                section.settings = {**section.settings, 'css_class': 'services'}
                section.save()

            if section.items.exists() and not replace:
                self.stdout.write(
                    f'  Skip [{lang}]: {section.items.count()} items already (use --replace to re-seed).'
                )
                continue

            section.items.all().delete()
            created_count = 0
            order = 0
            for filename, title, description in SERVICES_ROWS:
                src = SEED_DIR / filename
                if not src.is_file():
                    self.stderr.write(self.style.WARNING(f'  Missing file: {src}'))
                    continue
                item = SectionItem.objects.create(
                    section=section,
                    order=order,
                    title=title,
                    description=description,
                )
                order += 1
                created_count += 1
                storage_name = f'services/{filename}'
                with open(src, 'rb') as f:
                    item.image.save(storage_name, File(f), save=True)

            self.stdout.write(
                self.style.SUCCESS(f'  Seeded {created_count} service cards for [{lang}].')
            )

        self.stdout.write(self.style.SUCCESS('Services page seeding finished.'))
