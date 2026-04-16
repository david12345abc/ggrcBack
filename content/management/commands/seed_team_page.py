# -*- coding: utf-8 -*-
"""Create / update the /team page with staff cards; images from seed_assets/team/ or front/ggrc/temp/teams/."""
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from content.models import Page, PageSection, SectionItem

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp')

# management/commands -> content
CONTENT_DIR = Path(__file__).resolve().parent.parent.parent
SEED_DIR = CONTENT_DIR / 'seed_assets' / 'team'


def project_temp_teams_dir():
    """Repo root/front/ggrc/temp/teams (BASE_DIR is …/backend/ggrcBack)."""
    from django.conf import settings

    ggrc_back = Path(settings.BASE_DIR).resolve()
    repo_root = ggrc_back.parent.parent
    return repo_root / 'front' / 'ggrc' / 'temp' / 'teams'


def resolve_photo(stem, dirs):
    """Find an image file for stem '01-nino' or '01-nino.png' in dirs (first match)."""
    name = Path(stem).name
    stem_only = Path(name).stem
    for d in dirs:
        if not d or not d.is_dir():
            continue
        direct = d / name
        if direct.is_file():
            return direct
        for ext in IMAGE_EXTENSIONS:
            candidate = d / f'{stem_only}{ext}'
            if candidate.is_file():
                return candidate
    return None


def collect_sorted_images(d):
    if not d.is_dir():
        return []
    found = set()
    for ext in IMAGE_EXTENSIONS:
        found.update(d.glob(f'*{ext}'))
    return sorted(found, key=lambda p: p.name.lower())


# (image stem = basename without ext; files: Nino.png, LilitKarapetyan.png, Lilit.png, …)
# Fallback sorted pairing only if some stems are missing.
TEAM_ROWS = [
    ('Nino', 'Nino Museridze', 'Founder and Clinical Director of the GGRC Reproductive Center'),
    ('LilitKarapetyan', 'Lilit Karapetyan', 'Gynecologist-reproductive specialist'),
    ('Levon', 'Levon Vardazaryan', 'Urologist/andrologist'),
    ('Emma', 'Emma Vasilyan', 'Ultrasound Specialist'),
    ('Soma', 'Soma Hambardzumyan', 'Therapist'),
    ('Meri', 'Meri Ter-Stepanyan', 'Epidemiologist'),
    ('Lilit', 'Lilit Khachatryan', 'Nurse'),
    ('Siranush', 'Siranush Harutyunyan', 'Surgical Ward Nurse'),
    ('Anna', 'Anna Barseghyan', 'Head of the Sanitary Unit'),
    ('AnnaA', 'Anna Avetisyan', 'Administrator'),
    ('Maria', 'Maria Vardanyan', 'Coordinator'),
    ('Anahit', 'Anahit Kishmiryan', 'Senior Nurse'),
]

SECTION_I18N = {
    'en': {
        'title': 'OUR TEAM',
        'subtitle': 'The professional team at GGRC Armenia is your trusted partner on the journey to parenthood',
    },
    'ru': {
        'title': 'НАША КОМАНДА',
        'subtitle': (
            'Профессиональная команда GGRC Armenia — ваш надёжный партнёр на пути к родительству'
        ),
    },
    'am': {
        'title': '\u0544\u0565\u0580 \u0569\u056b\u0574\u0568',
        'subtitle': (
            'GGRC Armenia-\u056b \u0574\u0561\u057d\u0576\u0561\u056f\u0561\u0576 \u0569\u056b\u0574\u0568\u0576 '
            '\u0567 \u0570\u0561\u0575\u0561\u057d\u057f\u0561\u056f\u0561\u0576 \u0563\u0578\u0582\u0572\u0561\u0562\u0561\u0575\u0568 '
            '\u0574\u0561\u0574\u0578\u0582\u057d \u0578\u0582\u0572\u0561\u0580\u0578\u0582\u0569\u0575\u0561\u0576 \u0578\u0582\u0572\u056b \u0567'
        ),
    },
}


class Command(BaseCommand):
    help = (
        'Create / update Team page sections and staff cards. '
        'Place photos in content/seed_assets/team/ or front/ggrc/temp/teams/ '
        '(see TEAM_ROWS stems or same count of files for sorted pairing).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Remove existing team items on the Team page and re-import.',
        )

    def handle(self, *args, **options):
        replace = options['replace']
        temp_dir = project_temp_teams_dir()
        search_dirs = (SEED_DIR, temp_dir)

        if not SEED_DIR.is_dir():
            self.stderr.write(self.style.WARNING(f'Create folder and add images: {SEED_DIR}'))
        if not temp_dir.is_dir():
            self.stdout.write(f'  (No temp folder yet: {temp_dir})')

        page, _ = Page.objects.update_or_create(
            slug='team',
            defaults={
                'title': 'Our Team',
                'order': 3,
                'show_in_nav': True,
                'meta_description': 'GGRC Armenia medical team and specialists.',
            },
        )

        # Pre-compute file list if named files are incomplete
        named_pairs = []
        for stem, title, desc in TEAM_ROWS:
            named_pairs.append((resolve_photo(stem, search_dirs), title, desc))

        missing_ix = [i for i, (p, _, _) in enumerate(named_pairs) if p is None]
        seed_files = collect_sorted_images(SEED_DIR)
        temp_files = collect_sorted_images(temp_dir)
        if len(seed_files) >= len(TEAM_ROWS):
            sorted_pool = seed_files
        elif len(temp_files) >= len(TEAM_ROWS):
            sorted_pool = temp_files
        else:
            sorted_pool = (
                seed_files if len(seed_files) >= len(temp_files) else temp_files
            ) or seed_files or temp_files

        if missing_ix and len(sorted_pool) >= len(TEAM_ROWS):
            self.stdout.write(
                self.style.WARNING(
                    f'  Using {len(sorted_pool)} images sorted by filename (pairing to TEAM_ROWS order). '
                    'Rename files to match stems in seed_team_page.py for explicit mapping.'
                )
            )
            named_pairs = [
                (sorted_pool[i], TEAM_ROWS[i][1], TEAM_ROWS[i][2]) for i in range(len(TEAM_ROWS))
            ]
        elif missing_ix and len(sorted_pool) > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'  Partial import: {len(sorted_pool)} image(s) paired to the first rows in TEAM_ROWS '
                    f'({len(TEAM_ROWS) - len(sorted_pool)} without photo). Add files or rename to stems.'
                )
            )
            named_pairs = []
            for i in range(len(TEAM_ROWS)):
                if i < len(sorted_pool):
                    named_pairs.append(
                        (sorted_pool[i], TEAM_ROWS[i][1], TEAM_ROWS[i][2])
                    )
                else:
                    named_pairs.append((None, TEAM_ROWS[i][1], TEAM_ROWS[i][2]))
        elif missing_ix:
            for i in missing_ix:
                stem = TEAM_ROWS[i][0]
                self.stderr.write(
                    self.style.WARNING(
                        f'  Missing image for row {i + 1} ({stem}). '
                        f'Expected under {SEED_DIR} or {temp_dir}'
                    )
                )

        for lang, labels in SECTION_I18N.items():
            section, created = PageSection.objects.get_or_create(
                page=page,
                language=lang,
                section_type='team',
                defaults={
                    'order': 1,
                    'title': labels['title'],
                    'subtitle': labels['subtitle'],
                    'settings': {'css_class': 'team'},
                },
            )
            if not created:
                section.title = labels['title']
                section.subtitle = labels['subtitle']
                section.order = 1
                section.settings = {**section.settings, 'css_class': 'team'}
                section.save()

            if section.items.exists() and not replace:
                self.stdout.write(
                    f'  Skip [{lang}]: {section.items.count()} items already (use --replace to re-seed).'
                )
                continue

            section.items.all().delete()
            created_count = 0
            order = 0
            for src_path, title, description in named_pairs:
                item = SectionItem.objects.create(
                    section=section,
                    order=order,
                    title=title,
                    description=description,
                    link_url='',
                    link_text='',
                )
                order += 1
                created_count += 1
                if src_path and src_path.is_file():
                    storage_name = f'team/{src_path.name}'
                    with open(src_path, 'rb') as f:
                        item.image.save(storage_name, File(f), save=True)

            self.stdout.write(
                self.style.SUCCESS(f'  Seeded {created_count} team cards for [{lang}].')
            )

        self.stdout.write(self.style.SUCCESS('Team page seeding finished.'))
