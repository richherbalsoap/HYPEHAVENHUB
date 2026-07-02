"""
Seeds CountrySetting with a large list of countries: name, ISO code,
currency code/symbol, and a sensible default language pulled from
LANGUAGE_CHOICES. Shipping charge defaults to 0.00 and is left for the
store owner to set per country (see admin -> Countries).

Run with:
    python manage.py seed_countries

Safe to re-run: existing countries (matched by `code`) are left untouched
unless --update is passed, in which case currency/symbol/language are
refreshed but shipping_charge is never overwritten.
"""
from django.core.management.base import BaseCommand
from store.models import CountrySetting

# (name, ISO-2 code, currency code, currency symbol, default_language)
COUNTRIES = [
    ("India", "IN", "INR", "₹", "hi"),
    ("United States", "US", "USD", "$", "en"),
    ("United Kingdom", "GB", "GBP", "£", "en"),
    ("Canada", "CA", "CAD", "$", "en"),
    ("Australia", "AU", "AUD", "$", "en"),
    ("Germany", "DE", "EUR", "€", "de"),
    ("France", "FR", "EUR", "€", "fr"),
    ("Italy", "IT", "EUR", "€", "it"),
    ("Spain", "ES", "EUR", "€", "es"),
    ("Netherlands", "NL", "EUR", "€", "nl"),
    ("Portugal", "PT", "EUR", "€", "pt"),
    ("Greece", "GR", "EUR", "€", "el"),
    ("Poland", "PL", "PLN", "zł", "pl"),
    ("Switzerland", "CH", "CHF", "CHF", "de"),
    ("Sweden", "SE", "SEK", "kr", "en"),
    ("Norway", "NO", "NOK", "kr", "en"),
    ("Denmark", "DK", "DKK", "kr", "en"),
    ("Ireland", "IE", "EUR", "€", "en"),
    ("Belgium", "BE", "EUR", "€", "fr"),
    ("Austria", "AT", "EUR", "€", "de"),
    ("Turkey", "TR", "TRY", "₺", "tr"),
    ("Russia", "RU", "RUB", "₽", "ru"),
    ("United Arab Emirates", "AE", "AED", "د.إ", "ar"),
    ("Saudi Arabia", "SA", "SAR", "﷼", "ar"),
    ("Qatar", "QA", "QAR", "﷼", "ar"),
    ("Kuwait", "KW", "KWD", "د.ك", "ar"),
    ("Israel", "IL", "ILS", "₪", "he"),
    ("Egypt", "EG", "EGP", "£", "ar"),
    ("South Africa", "ZA", "ZAR", "R", "en"),
    ("Nigeria", "NG", "NGN", "₦", "en"),
    ("Kenya", "KE", "KES", "KSh", "sw"),
    ("China", "CN", "CNY", "¥", "zh"),
    ("Hong Kong", "HK", "HKD", "$", "zh"),
    ("Taiwan", "TW", "TWD", "$", "zh"),
    ("Japan", "JP", "JPY", "¥", "ja"),
    ("South Korea", "KR", "KRW", "₩", "ko"),
    ("Singapore", "SG", "SGD", "$", "en"),
    ("Malaysia", "MY", "MYR", "RM", "ms"),
    ("Indonesia", "ID", "IDR", "Rp", "id"),
    ("Thailand", "TH", "THB", "฿", "th"),
    ("Vietnam", "VN", "VND", "₫", "vi"),
    ("Philippines", "PH", "PHP", "₱", "en"),
    ("Pakistan", "PK", "PKR", "₨", "ur"),
    ("Bangladesh", "BD", "BDT", "৳", "bn"),
    ("Sri Lanka", "LK", "LKR", "₨", "ta"),
    ("Nepal", "NP", "NPR", "₨", "hi"),
    ("New Zealand", "NZ", "NZD", "$", "en"),
    ("Brazil", "BR", "BRL", "R$", "pt"),
    ("Mexico", "MX", "MXN", "$", "es"),
    ("Argentina", "AR", "ARS", "$", "es"),
    ("Chile", "CL", "CLP", "$", "es"),
    ("Colombia", "CO", "COP", "$", "es"),
    ("Peru", "PE", "PEN", "S/", "es"),
    ("Finland", "FI", "EUR", "€", "en"),
    ("Czech Republic", "CZ", "CZK", "Kč", "en"),
    ("Romania", "RO", "RON", "lei", "en"),
    ("Ukraine", "UA", "UAH", "₴", "ru"),
    ("Iran", "IR", "IRR", "﷼", "fa"),
    ("Iraq", "IQ", "IQD", "ع.د", "ar"),
]


class Command(BaseCommand):
    help = "Seed CountrySetting with major world countries (currency + language). Prices are NOT set — add per-product prices in admin > Products > Prices."

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Also refresh name/currency/symbol/language for countries that already exist (shipping_charge is never touched).',
        )

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for name, code, currency_code, currency_symbol, default_language in COUNTRIES:
            existing = CountrySetting.objects.filter(code=code).first()
            if existing:
                if options['update']:
                    existing.name = name
                    existing.currency_code = currency_code
                    existing.currency_symbol = currency_symbol
                    existing.default_language = default_language
                    existing.save()
                    updated_count += 1
                else:
                    skipped_count += 1
                continue

            CountrySetting.objects.create(
                name=name,
                code=code,
                currency_code=currency_code,
                currency_symbol=currency_symbol,
                default_language=default_language,
                shipping_charge=0.00,
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Countries seeded: {created_count} created, {updated_count} updated, {skipped_count} already existed (skipped)."
        ))
        self.stdout.write(
            "Ab admin panel me jaake har country ke liye: 1) shipping charge set karo, "
            "2) har product ke 'Manage Prices' page pe jaake us country ka price daalo."
        )
