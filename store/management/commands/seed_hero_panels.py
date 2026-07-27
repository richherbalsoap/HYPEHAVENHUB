from django.core.management.base import BaseCommand
from store.models import HeroPanel

class Command(BaseCommand):
    help = 'Seeds initial 4 default Hero Panels if table is empty'

    def handle(self, *args, **kwargs):
        if HeroPanel.objects.exists():
            self.stdout.write(self.style.SUCCESS('HeroPanel records already exist. Skipping seed.'))
            return

        defaults = [
            {
                'title': 'Ruby Stone Long Jhumka',
                'background_text': 'RUBY STONE LONG JHUMKA',
                'image_url': '/static/images/img1.webp',
                'bg_color': '#7C1F45',
                'panel_color': '#9A2E5B',
                'order': 1,
                'is_active': True,
            },
            {
                'title': 'Kashmiri Long Chain Jhumka',
                'background_text': 'KASHMIRI LONG CHAIN JHUMKA',
                'image_url': '/static/images/img2.webp',
                'bg_color': '#28553A',
                'panel_color': '#38724D',
                'order': 2,
                'is_active': True,
            },
            {
                'title': 'Kundan Pearl Jhumka',
                'background_text': 'KUNDAN PEARL JHUMKA',
                'image_url': '/static/images/img3.webp',
                'bg_color': '#A97A2E',
                'panel_color': '#C4954B',
                'order': 3,
                'is_active': True,
            },
            {
                'title': 'Rose Pearl Studs',
                'background_text': 'ROSE PEARL STUDS',
                'image_url': '/static/images/img4.webp',
                'bg_color': '#C97B95',
                'panel_color': '#D998AE',
                'order': 4,
                'is_active': True,
            },
        ]

        for item in defaults:
            HeroPanel.objects.create(**item)

        self.stdout.write(self.style.SUCCESS('Successfully seeded 4 default Hero Panels!'))
