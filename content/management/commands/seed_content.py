import os
import shutil
from django.conf import settings
from django.core.management.base import BaseCommand
from content.models import User, Page, PageSection, SectionItem, SiteSettings


IMAGES_SRC = os.path.join(settings.BASE_DIR, '..', 'ggrc', 'public', 'images')


def copy_image(relative_path, dest_subdir='seed'):
    """Copy image from public/images/ to MEDIA_ROOT and return the media-relative path."""
    src = os.path.normpath(os.path.join(IMAGES_SRC, relative_path))
    if not os.path.exists(src):
        return ''
    dest_rel = os.path.join(dest_subdir, relative_path).replace('\\', '/')
    dest_abs = os.path.join(settings.MEDIA_ROOT, dest_rel)
    os.makedirs(os.path.dirname(dest_abs), exist_ok=True)
    shutil.copy2(src, dest_abs)
    return dest_rel


class Command(BaseCommand):
    help = 'Seed the database with initial content from the React frontend'

    def handle(self, *args, **options):
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        # ── Superadmin ────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@ggrc.am',
                password='admin123',
                role='superadmin',
            )
            self.stdout.write(self.style.SUCCESS('Created superadmin: admin / admin123'))

        # ── Site Settings ─────────────────────────────────────────
        ss = SiteSettings.load()
        ss.address = 'Armenia, Yerevan Abovyan 56/4'
        ss.address_short = 'Armenia Yerevan Abovyan 56/4'
        ss.phones = ['+374 95520055', '+374 60530055']
        ss.phone_display = '+374 95520055 , +374 60530055'
        ss.email = 'ggrcarmenia@gmail.com'
        ss.instagram_url = 'https://instagram.com'
        ss.linkedin_url = 'https://linkedin.com'
        ss.facebook_url = 'https://facebook.com'
        ss.youtube_video_id = 'Wu2lM_yjkzc'
        logo = copy_image('logo.png')
        if logo:
            ss.logo = logo
        logo_p = copy_image('logo-purple.png')
        if logo_p:
            ss.logo_purple = logo_p
        ss.save()
        self.stdout.write(self.style.SUCCESS('Site settings saved'))

        # ── Pages ─────────────────────────────────────────────────
        home, _ = Page.objects.update_or_create(slug='home', defaults={'title': 'Home', 'order': 0})
        about, _ = Page.objects.update_or_create(slug='about', defaults={'title': 'About Us', 'order': 1})

        # Clear existing sections for idempotency
        PageSection.objects.filter(page__in=[home, about]).delete()

        # ── HOME PAGE ─────────────────────────────────────────────
        order = 0

        # Hero
        order += 1
        hero = PageSection.objects.create(
            page=home, section_type='hero', order=order,
            title='THE DREAM OF PARENTHOOD COMES TRUE HERE',
            settings={'css_class': 'hero'},
        )
        SectionItem.objects.create(
            section=hero, order=0, title='Hero Image',
            image=copy_image('doctors-hero.png'),
        )

        # Features Carousel
        order += 1
        features = PageSection.objects.create(
            page=home, section_type='features_carousel', order=order,
            title='', settings={'css_class': 'features'},
        )
        features_data = [
            {'icon_name': 'FaUserMd', 'title': 'Professional Excellence',
             'description': 'We bring together specialists with international experience who follow the latest advancements in reproductive medicine.'},
            {'icon_name': 'FaHospital', 'title': 'Advanced Technology',
             'description': 'Our clinic is equipped with state-of-the-art technology including Time-lapse Embryoscope and AI-integrated IVF systems.'},
            {'icon_name': 'FaHandHoldingHeart', 'title': 'Personalized Care',
             'description': 'Every patient receives an individualized treatment plan tailored to their unique medical needs and personal circumstances.'},
            {'icon_name': 'FaGlobe', 'title': 'International Standards',
             'description': 'As a branch of the renowned Georgian-German Reproductive Center, we maintain the highest international standards of care.'},
        ]
        for i, f in enumerate(features_data):
            SectionItem.objects.create(
                section=features, order=i,
                title=f['title'], description=f['description'],
                icon_name=f['icon_name'],
            )

        # About Teaser
        order += 1
        about_teaser = PageSection.objects.create(
            page=home, section_type='about_teaser', order=order,
            title='ABOUT US',
            settings={
                'css_class': 'about',
                'bold_text': 'GGRC Armenia is the Armenian branch of the internationally renowned Georgian-German Reproductive Center (GGRC), a leading fertility clinic that has helped countless families fulfill their dream of becoming parents.',
                'text': 'Our core mission is to make advanced, high-quality, and effective reproductive services accessible to everyone facing infertility challenges.',
                'button_text': 'About Us',
                'button_link': '/about',
            },
        )
        SectionItem.objects.create(
            section=about_teaser, order=0, title='About Image',
            image=copy_image('about-interview.png'),
        )
        highlights = [
            'Time-lapse Embryoscope',
            'Preimplantation Genetic Testing (PGT)',
            'Cryopreservation of eggs and sperm',
            'Integration of Artificial Intelligence (AI) in IVF (IVF/ICSI)',
        ]
        for i, h in enumerate(highlights):
            SectionItem.objects.create(
                section=about_teaser, order=i + 1,
                title=h, extra_data={'type': 'highlight'},
            )

        # Services
        order += 1
        services = PageSection.objects.create(
            page=home, section_type='services', order=order,
            title='OUR SERVICES',
            subtitle='GGRC Armenia offers a wide range of services, including',
            settings={'css_class': 'services'},
        )
        SectionItem.objects.create(
            section=services, order=0,
            title='INFERTILITY DIAGNOSIS AND TREATMENT (FOR WOMEN AND MEN)',
            image=copy_image('hands.png'),
        )

        # Why Choose Us
        order += 1
        why = PageSection.objects.create(
            page=home, section_type='why_choose_us', order=order,
            title='WHY CHOOSE US',
            settings={'css_class': 'why-choose'},
        )
        reasons = [
            {'icon_name': 'FaAward', 'title': 'Quality Care',
             'desc': 'Our clinic upholds the highest standards of medical care and patient safety.'},
            {'icon_name': 'FaMicroscope', 'title': 'Advanced Equipment',
             'desc': 'We use cutting-edge medical technology and modern laboratory systems.'},
            {'icon_name': 'FaGlobeAmericas', 'title': 'Multilingual Staff',
             'desc': 'Our team speaks multiple languages to serve international patients.'},
            {'icon_name': 'FaHeart', 'title': 'Personalized Care',
             'desc': 'Each patient receives a customized treatment plan based on their needs.'},
            {'icon_name': 'FaUsers', 'title': 'Emotional Support',
             'desc': 'Comprehensive emotional and psychological support throughout your journey.'},
            {'icon_name': 'FaPray', 'title': 'Cultural Sensitivity',
             'desc': 'Deep understanding and respect for diverse cultural backgrounds.'},
        ]
        for i, r in enumerate(reasons):
            SectionItem.objects.create(
                section=why, order=i,
                title=r['title'], description=r['desc'],
                icon_name=r['icon_name'],
            )

        # Team
        order += 1
        team = PageSection.objects.create(
            page=home, section_type='team', order=order,
            title='OUR TEAM',
            subtitle='The professional team at GGRC Armenia is Your trusted partner on the journey to parenthood',
            settings={'css_class': 'team'},
        )
        members = [
            {'name': 'Nino Museridze', 'role': 'Founder and Clinical Director of the GGRC', 'img': 'team/nino.png'},
            {'name': 'Lilit Karapetyan', 'role': 'Gynecologist-reproductive specialist', 'img': 'team/lilit.png'},
            {'name': 'Levon Vardazaryan', 'role': 'Urologist/andrologist', 'img': 'team/levon.png'},
            {'name': 'Emma Vasilyan', 'role': 'Ultrasound Specialist', 'img': 'team/emma.png'},
        ]
        for i, m in enumerate(members):
            SectionItem.objects.create(
                section=team, order=i,
                title=m['name'], description=m['role'],
                image=copy_image(m['img']),
            )

        # Steps
        order += 1
        steps = PageSection.objects.create(
            page=home, section_type='steps', order=order,
            title='STEPS',
            settings={'css_class': 'steps'},
        )
        steps_data = [
            {'number': '01', 'title': 'Get an Appointment',
             'desc': 'Start Your journey to parenthood with the guidance of experienced specialists',
             'img': 'steps/step1.png'},
            {'number': '02', 'title': 'Start Check-Up',
             'desc': "We'll carefully assess Your reproductive health",
             'img': 'steps/step2.png'},
            {'number': '03', 'title': 'Enjoy a Healthy Life',
             'desc': 'Our goal is to help You build a complete and happy family',
             'img': 'steps/step3.png'},
        ]
        for i, s in enumerate(steps_data):
            SectionItem.objects.create(
                section=steps, order=i,
                title=s['title'], description=s['desc'],
                image=copy_image(s['img']),
                extra_data={'number': s['number']},
            )

        # Testimonials
        order += 1
        testimonials = PageSection.objects.create(
            page=home, section_type='testimonials', order=order,
            title='PATIENTS ABOUT GGRC ARMENIA',
            background_image=copy_image('neural-network.jpg'),
            settings={'css_class': 'testimonials'},
        )
        reviews = [
            {'text': "I had PCOS and hormonal disorders. We had attempted IVF multiple times in Russia, but without success. At GGRC Armenia, the impossible became possible. I'm honestly impressed by the level of professionalism in such a small country.",
             'author': 'Patient from Russia'},
            {'text': 'The team at GGRC Armenia treated us with such warmth and care. After years of trying, we finally became parents. We are forever grateful for their expertise and dedication.',
             'author': 'International Patient'},
            {'text': 'From the very first consultation, we felt that we were in good hands. The doctors explained every step clearly and gave us hope when we had almost given up.',
             'author': 'Patient from CIS'},
        ]
        for i, r in enumerate(reviews):
            SectionItem.objects.create(
                section=testimonials, order=i,
                description=r['text'],
                extra_data={'author': r['author']},
            )

        # Blog
        order += 1
        blog = PageSection.objects.create(
            page=home, section_type='blog', order=order,
            title='BLOG',
            settings={'css_class': 'blog'},
        )
        posts = [
            {'title': 'With Confident Steps Toward the Joy of Parenthood: The Official Opening of GGRC Armenia',
             'img': 'blog/opening.jpg', 'link': '#'},
            {'title': 'Modern Approaches to Infertility Treatment: Professional Conference Initiated by GGRC Armenia',
             'img': 'blog/vodnom.jpg', 'link': '#'},
            {'title': '\u201CAravot Luso\u201D on Armenian Public TV: GGRC Armenia: A New Hope in Reproductive Medicine',
             'img': 'blog/interview-tv.png', 'link': '#'},
        ]
        for i, p in enumerate(posts):
            SectionItem.objects.create(
                section=blog, order=i,
                title=p['title'],
                image=copy_image(p['img']),
                link_url=p['link'], link_text='READ MORE',
            )

        # ── ABOUT PAGE ────────────────────────────────────────────
        order = 0

        # About Hero Text
        order += 1
        PageSection.objects.create(
            page=about, section_type='about_hero_text', order=order,
            title='IN TRUSTED HANDS \u2013 STEP BY STEP TOWARD THE MIRACLE OF NEW LIFE',
            subtitle='',
            settings={
                'kicker': 'ABOUT US',
                'lead': (
                    'With the growing demand for innovative reproductive treatments in Armenia, '
                    'GGRC Armenia, a Georgian-German-Armenian international reproductive center, '
                    'brings the latest generation of technologies, including those powered by artificial '
                    'intelligence, along with a fully personalized approach to care. Our newly opened '
                    'clinic is equipped with cutting-edge medical technologies and is fully focused on '
                    'diagnostics, in vitro fertilization (IVF/ICSI), treatment of both female and male '
                    'infertility, and the promotion of reproductive health.'
                ),
            },
        )

        # About Values
        order += 1
        values_section = PageSection.objects.create(
            page=about, section_type='about_values', order=order,
            title='OUR VALUES',
        )
        values = [
            {'title': 'Professional Excellence',
             'text': 'We bring together specialists with international experience who follow the latest advancements in reproductive medicine.'},
            {'title': 'Innovation',
             'text': 'We apply cutting-edge technologies, including artificial intelligence, to enhance the accuracy and effectiveness of treatment.'},
            {'title': 'Accessibility',
             'text': "We believe that high-quality reproductive healthcare should be accessible to everyone. That\u2019s why we offer financial support programs to ease the burden for couples."},
            {'title': 'Education & Development',
             'text': 'Through conferences, seminars, and workshops, we aim to enrich the medical community in Armenia and across the region.'},
            {'title': 'International Collaboration',
             'text': 'We build strong bridges between local and global experts to foster collective progress in reproductive medicine.'},
        ]
        for i, v in enumerate(values):
            SectionItem.objects.create(
                section=values_section, order=i,
                title=v['title'], description=v['text'],
            )

        # About Tech
        order += 1
        tech_section = PageSection.objects.create(
            page=about, section_type='about_tech', order=order,
            title='INNOVATIVE TECHNOLOGIES FOR MAXIMUM EFFECTIVENESS',
            settings={
                'body': (
                    'At GGRC Armenia, we confidently claim to be shaping the future of reproductive medicine by '
                    'combining years of clinical experience with cutting-edge AI technologies. Our mission is not '
                    'only to replace uncertainty with hope but also to offer couples the most effective, '
                    'personalized, and scientifically grounded infertility treatments available. We firmly believe '
                    'that the future of in vitro fertilization (IVF/ICSI) lies at the intersection of advanced '
                    'medical expertise, deep knowledge, and next-generation technologies. Through these '
                    'innovations, GGRC Armenia is setting new standards in the Armenian reproductive healthcare landscape.'
                ),
            },
        )
        SectionItem.objects.create(
            section=tech_section, order=0, title='Tech Image',
            image=copy_image('about-woman-seated.png'),
            extra_data={'type': 'media'},
        )
        tech_items = [
            {'title': 'Time-lapse Embryoscope',
             'text': 'An innovative embryo incubation system that continuously monitors embryo development 24/7, allowing embryologists to select the highest-quality embryo for implantation.'},
            {'title': 'Preimplantation Genetic Testing (PGT)',
             'text': 'A genetic screening method for embryos that increases the chances of a healthy pregnancy and reduces the risk of genetic disorders.'},
            {'title': 'Cryopreservation of eggs and sperm',
             'text': 'A biological preservation method that allows individuals and couples to safeguard their reproductive potential for the future.'},
            {'title': 'Integration of Artificial Intelligence (AI) in IVF (IVF/ICSI)',
             'text': 'A unique innovation in the region, where AI systems are applied throughout all stages of the IVF process. This technology significantly streamlines clinical decision-making while enhancing treatment success rates.'},
        ]
        for i, t in enumerate(tech_items):
            SectionItem.objects.create(
                section=tech_section, order=i + 1,
                title=t['title'], description=t['text'],
            )

        # About Video
        order += 1
        PageSection.objects.create(
            page=about, section_type='about_video', order=order,
            title='',
            settings={
                'youtube_channel': 'https://www.youtube.com/channel/UCvhOxd4DL1kUZLOPJV-K-aA',
                'fallback_image': copy_image('blog/interview-tv.png'),
            },
        )

        # About Conference
        order += 1
        conf_section = PageSection.objects.create(
            page=about, section_type='about_conference', order=order,
            title='A NEW CHAPTER IN INTERNATIONAL SCIENTIFIC AND MEDICAL COLLABORATION IN ARMENIA',
        )
        bullets = [
            'On March 9, 2025, GGRC Armenia hosted its first scientific-medical conference, bringing together leading reproductive medicine experts from across the region. This milestone event marked a significant step not only in GGRC Armenia\u2019s growth but also in strengthening cooperation between local and international medical communities.',
            'Throughout the conference, participants discussed the latest advancements in reproductive medicine, innovative technologies, and future perspectives for infertility treatment. The event played a key role in fostering knowledge exchange and enhancing the quality of reproductive care across the region.',
            'GGRC Armenia emphasizes that scientific and educational initiatives are just as vital as the delivery of medical services. The center is committed to advancing medical education in Armenia, equipping the local medical community with cutting-edge knowledge and skills.',
        ]
        for i, b in enumerate(bullets):
            SectionItem.objects.create(
                section=conf_section, order=i,
                description=b,
            )

        self.stdout.write(self.style.SUCCESS('Content seeded successfully!'))
