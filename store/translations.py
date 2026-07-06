"""
Simple dictionary-based translation system for storefront UI text.

Why this exists: the site previously saved a "language" choice into the
session but never actually translated anything with it — selecting a
language changed nothing on the page. This module provides real
translations for the core storefront strings (nav, buttons, cart,
checkout, common labels) for every language in LANGUAGE_CHOICES.

Usage in templates:
    {% load i18n_store %}
    {% t "add_to_cart" %}

Usage in Python:
    from store.translations import translate
    translate(request, "add_to_cart")

Any key not present for the active language automatically falls back to
English, and any key not present at all just returns the key itself
(visibly obvious in testing, never a hard crash).
"""

TRANSLATIONS = {
    "add_to_cart": {
        "en": "Add to Cart", "hi": "कार्ट में डालें", "zh": "加入购物车", "es": "Añadir al carrito",
        "fr": "Ajouter au panier", "ar": "أضف إلى السلة", "pt": "Adicionar ao carrinho",
        "de": "In den Warenkorb", "ja": "カートに追加", "ru": "В корзину", "bn": "কার্টে যোগ করুন",
        "ur": "کارٹ میں شامل کریں", "id": "Tambah ke Keranjang", "it": "Aggiungi al carrello",
        "ko": "장바구니에 담기", "tr": "Sepete Ekle", "vi": "Thêm vào giỏ hàng", "th": "เพิ่มลงตะกร้า",
        "nl": "In winkelwagen", "pl": "Dodaj do koszyka", "fa": "افزودن به سبد خرید",
        "sw": "Ongeza kwenye Kikapu", "ta": "கார்ட்டில் சேர்", "te": "కార్ట్‌కు జోడించండి",
        "mr": "कार्टमध्ये जोडा", "gu": "કાર્ટમાં ઉમેરો", "pa": "ਕਾਰਟ ਵਿੱਚ ਸ਼ਾਮਲ ਕਰੋ",
        "ms": "Tambah ke Troli", "he": "הוסף לעגלה", "el": "Προσθήκη στο καλάθι",
    },
    "buy_now": {
        "en": "Buy Now", "hi": "अभी खरीदें", "zh": "立即购买", "es": "Comprar ahora",
        "fr": "Acheter maintenant", "ar": "اشتر الآن", "pt": "Comprar agora", "de": "Jetzt kaufen",
        "ja": "今すぐ購入", "ru": "Купить сейчас", "bn": "এখনই কিনুন", "ur": "ابھی خریدیں",
        "id": "Beli Sekarang", "it": "Acquista ora", "ko": "지금 구매", "tr": "Şimdi Satın Al",
        "vi": "Mua ngay", "th": "ซื้อเลย", "nl": "Nu kopen", "pl": "Kup teraz",
        "fa": "همین حالا بخرید", "sw": "Nunua Sasa", "ta": "இப்போது வாங்க", "te": "ఇప్పుడు కొనండి",
        "mr": "आता खरेदी करा", "gu": "હમણાં ખરીદો", "pa": "ਹੁਣੇ ਖਰੀਦੋ", "ms": "Beli Sekarang",
        "he": "קנה עכשיו", "el": "Αγορά τώρα",
    },
    "home": {
        "en": "Home", "hi": "होम", "zh": "首页", "es": "Inicio", "fr": "Accueil", "ar": "الرئيسية",
        "pt": "Início", "de": "Startseite", "ja": "ホーム", "ru": "Главная", "bn": "হোম",
        "ur": "ہوم", "id": "Beranda", "it": "Home", "ko": "홈", "tr": "Ana Sayfa", "vi": "Trang chủ",
        "th": "หน้าแรก", "nl": "Home", "pl": "Strona główna", "fa": "خانه", "sw": "Nyumbani",
        "ta": "முகப்பு", "te": "హోమ్", "mr": "मुख्यपृष्ठ", "gu": "હોમ", "pa": "ਹੋਮ",
        "ms": "Laman Utama", "he": "בית", "el": "Αρχική",
    },
    "shop": {
        "en": "Shop", "hi": "शॉप", "zh": "商店", "es": "Tienda", "fr": "Boutique", "ar": "المتجر",
        "pt": "Loja", "de": "Shop", "ja": "ショップ", "ru": "Магазин", "bn": "দোকান", "ur": "دکان",
        "id": "Belanja", "it": "Negozio", "ko": "쇼핑", "tr": "Mağaza", "vi": "Cửa hàng",
        "th": "ร้านค้า", "nl": "Winkel", "pl": "Sklep", "fa": "فروشگاه", "sw": "Duka",
        "ta": "கடை", "te": "షాప్", "mr": "दुकान", "gu": "દુકાન", "pa": "ਦੁਕਾਨ",
        "ms": "Kedai", "he": "חנות", "el": "Κατάστημα",
    },
    "cart": {
        "en": "Cart", "hi": "कार्ट", "zh": "购物车", "es": "Carrito", "fr": "Panier", "ar": "السلة",
        "pt": "Carrinho", "de": "Warenkorb", "ja": "カート", "ru": "Корзина", "bn": "কার্ট",
        "ur": "کارٹ", "id": "Keranjang", "it": "Carrello", "ko": "장바구니", "tr": "Sepet",
        "vi": "Giỏ hàng", "th": "ตะกร้า", "nl": "Winkelwagen", "pl": "Koszyk", "fa": "سبد خرید",
        "sw": "Kikapu", "ta": "கார்ட்", "te": "కార్ట్", "mr": "कार्ट", "gu": "કાર્ટ", "pa": "ਕਾਰਟ",
        "ms": "Troli", "he": "עגלה", "el": "Καλάθι",
    },
    "checkout": {
        "en": "Checkout", "hi": "चेकआउट", "zh": "结账", "es": "Pagar", "fr": "Commander",
        "ar": "الدفع", "pt": "Finalizar compra", "de": "Zur Kasse", "ja": "レジに進む",
        "ru": "Оформить заказ", "bn": "চেকআউট", "ur": "چیک آؤٹ", "id": "Checkout",
        "it": "Checkout", "ko": "결제하기", "tr": "Ödeme", "vi": "Thanh toán", "th": "ชำระเงิน",
        "nl": "Afrekenen", "pl": "Do kasy", "fa": "پرداخت", "sw": "Malizia", "ta": "செக்அவுட்",
        "te": "చెక్అవుట్", "mr": "चेकआउट", "gu": "ચેકઆઉટ", "pa": "ਚੈੱਕਆਉਟ", "ms": "Checkout",
        "he": "לתשלום", "el": "Ολοκλήρωση αγοράς",
    },
    "my_orders": {
        "en": "My Orders", "hi": "मेरे ऑर्डर", "zh": "我的订单", "es": "Mis pedidos",
        "fr": "Mes commandes", "ar": "طلباتي", "pt": "Meus pedidos", "de": "Meine Bestellungen",
        "ja": "注文履歴", "ru": "Мои заказы", "bn": "আমার অর্ডার", "ur": "میرے آرڈرز",
        "id": "Pesanan Saya", "it": "I miei ordini", "ko": "내 주문", "tr": "Siparişlerim",
        "vi": "Đơn hàng của tôi", "th": "คำสั่งซื้อของฉัน", "nl": "Mijn bestellingen",
        "pl": "Moje zamówienia", "fa": "سفارش‌های من", "sw": "Maagizo Yangu", "ta": "எனது ஆர்டர்கள்",
        "te": "నా ఆర్డర్‌లు", "mr": "माझ्या ऑर्डर्स", "gu": "મારા ઓર્ડર", "pa": "ਮੇਰੇ ਆਰਡਰ",
        "ms": "Pesanan Saya", "he": "ההזמנות שלי", "el": "Οι παραγγελίες μου",
    },
    "wishlist": {
        "en": "Wishlist", "hi": "विशलिस्ट", "zh": "心愿单", "es": "Lista de deseos",
        "fr": "Liste de souhaits", "ar": "قائمة الرغبات", "pt": "Lista de desejos",
        "de": "Wunschliste", "ja": "お気に入り", "ru": "Избранное", "bn": "উইশলিস্ট",
        "ur": "پسندیدہ فہرست", "id": "Wishlist", "it": "Lista dei desideri", "ko": "위시리스트",
        "tr": "İstek Listesi", "vi": "Danh sách yêu thích", "th": "รายการโปรด",
        "nl": "Verlanglijst", "pl": "Lista życzeń", "fa": "لیست علاقه‌مندی‌ها", "sw": "Orodha Tamani",
        "ta": "விருப்பப் பட்டியல்", "te": "వాంఛా జాబితా", "mr": "इच्छा यादी", "gu": "ઈચ્છા યાદી",
        "pa": "ਇੱਛਾ ਸੂਚੀ", "ms": "Senarai Hajat", "he": "רשימת משאלות", "el": "Λίστα επιθυμιών",
    },
    "search": {
        "en": "Search", "hi": "खोजें", "zh": "搜索", "es": "Buscar", "fr": "Rechercher",
        "ar": "بحث", "pt": "Pesquisar", "de": "Suchen", "ja": "検索", "ru": "Поиск",
        "bn": "অনুসন্ধান", "ur": "تلاش کریں", "id": "Cari", "it": "Cerca", "ko": "검색",
        "tr": "Ara", "vi": "Tìm kiếm", "th": "ค้นหา", "nl": "Zoeken", "pl": "Szukaj",
        "fa": "جستجو", "sw": "Tafuta", "ta": "தேடு", "te": "వెతకండి", "mr": "शोधा",
        "gu": "શોધો", "pa": "ਖੋਜੋ", "ms": "Cari", "he": "חיפוש", "el": "Αναζήτηση",
    },
    "login": {
        "en": "Login", "hi": "लॉगिन", "zh": "登录", "es": "Iniciar sesión", "fr": "Connexion",
        "ar": "تسجيل الدخول", "pt": "Entrar", "de": "Anmelden", "ja": "ログイン", "ru": "Войти",
        "bn": "লগইন", "ur": "لاگ ان", "id": "Masuk", "it": "Accedi", "ko": "로그인",
        "tr": "Giriş Yap", "vi": "Đăng nhập", "th": "เข้าสู่ระบบ", "nl": "Inloggen",
        "pl": "Zaloguj się", "fa": "ورود", "sw": "Ingia", "ta": "உள்நுழை", "te": "లాగిన్",
        "mr": "लॉगिन", "gu": "લોગિન", "pa": "ਲਾਗਇਨ", "ms": "Log Masuk", "he": "התחברות",
        "el": "Σύνδεση",
    },
    "total": {
        "en": "Total", "hi": "कुल", "zh": "总计", "es": "Total", "fr": "Total", "ar": "الإجمالي",
        "pt": "Total", "de": "Gesamt", "ja": "合計", "ru": "Итого", "bn": "মোট", "ur": "کل",
        "id": "Total", "it": "Totale", "ko": "합계", "tr": "Toplam", "vi": "Tổng cộng",
        "th": "รวม", "nl": "Totaal", "pl": "Suma", "fa": "مجموع", "sw": "Jumla", "ta": "மொத்தம்",
        "te": "మొత్తం", "mr": "एकूण", "gu": "કુલ", "pa": "ਕੁੱਲ", "ms": "Jumlah", "he": "סה\"כ",
        "el": "Σύνολο",
    },
    "shipping": {
        "en": "Shipping", "hi": "शिपिंग", "zh": "运费", "es": "Envío", "fr": "Livraison",
        "ar": "الشحن", "pt": "Envio", "de": "Versand", "ja": "配送", "ru": "Доставка",
        "bn": "শিপিং", "ur": "شپنگ", "id": "Pengiriman", "it": "Spedizione", "ko": "배송",
        "tr": "Kargo", "vi": "Vận chuyển", "th": "การจัดส่ง", "nl": "Verzending",
        "pl": "Wysyłka", "fa": "ارسال", "sw": "Usafirishaji", "ta": "ஷிப்பிங்", "te": "షిప్పింగ్",
        "mr": "शिपिंग", "gu": "શિપિંગ", "pa": "ਸ਼ਿਪਿੰਗ", "ms": "Penghantaran", "he": "משלוח",
        "el": "Αποστολή",
    },
    "select_your_country": {
        "en": "Choose your location", "hi": "अपना स्थान चुनें", "zh": "选择您的位置",
        "es": "Elige tu ubicación", "fr": "Choisissez votre emplacement",
        "ar": "اختر موقعك", "pt": "Escolha sua localização", "de": "Wählen Sie Ihren Standort",
        "ja": "所在地を選択してください", "ru": "Выберите ваше местоположение",
        "bn": "আপনার অবস্থান নির্বাচন করুন", "ur": "اپنا مقام منتخب کریں",
        "id": "Pilih lokasi Anda", "it": "Scegli la tua posizione", "ko": "위치를 선택하세요",
        "tr": "Konumunuzu seçin", "vi": "Chọn vị trí của bạn", "th": "เลือกตำแหน่งของคุณ",
        "nl": "Kies uw locatie", "pl": "Wybierz swoją lokalizację", "fa": "موقعیت خود را انتخاب کنید",
        "sw": "Chagua eneo lako", "ta": "உங்கள் இருப்பிடத்தைத் தேர்ந்தெடுக்கவும்",
        "te": "మీ స్థానాన్ని ఎంచుకోండి", "mr": "तुमचे स्थान निवडा", "gu": "તમારું સ્થાન પસંદ કરો",
        "pa": "ਆਪਣਾ ਟਿਕਾਣਾ ਚੁਣੋ", "ms": "Pilih lokasi anda", "he": "בחר את מיקומך",
        "el": "Επιλέξτε την τοποθεσία σας",
    },
    "out_of_stock": {
        "en": "Out of Stock", "hi": "स्टॉक में नहीं", "zh": "缺货", "es": "Agotado",
        "fr": "Rupture de stock", "ar": "غير متوفر", "pt": "Fora de estoque",
        "de": "Nicht auf Lager", "ja": "在庫切れ", "ru": "Нет в наличии", "bn": "স্টক নেই",
        "ur": "اسٹاک ختم", "id": "Stok Habis", "it": "Esaurito", "ko": "품절", "tr": "Stokta Yok",
        "vi": "Hết hàng", "th": "สินค้าหมด", "nl": "Niet op voorraad", "pl": "Brak w magazynie",
        "fa": "ناموجود", "sw": "Hazipo", "ta": "கையிருப்பில் இல்லை", "te": "స్టాక్ లేదు",
        "mr": "स्टॉक नाही", "gu": "સ્ટોકમાં નથી", "pa": "ਸਟਾਕ ਵਿੱਚ ਨਹੀਂ", "ms": "Stok Habis",
        "he": "אזל מהמלאי", "el": "Εξαντλήθηκε",
    },
    # Newly added keys
    "all_jewelry": {"en": "All Jewelry", "hi": "सभी आभूषण"},
    "offers": {"en": "Offers", "hi": "ऑफर"},
    "my_profile": {"en": "My Profile", "hi": "मेरी प्रोफ़ाइल"},
    "logout": {"en": "Logout", "hi": "लॉग आउट"},
    "sign_up": {"en": "Sign Up", "hi": "साइन अप"},
    "notifications": {"en": "Notifications", "hi": "सूचनाएं"},
    "settings": {"en": "Settings", "hi": "सेटिंग्स"},
    "addresses": {"en": "Addresses", "hi": "पते"},
    "site_title": {"en": "Handcrafted Indian Jewelry", "hi": "हस्तनिर्मित भारतीय आभूषण"},
    "free_delivery_above": {"en": "Free delivery on orders above", "hi": "से ऊपर के ऑर्डर पर मुफ़्त डिलीवरी"},
    "use_code_jhumka": {"en": "Use code JHUMKA10 for 10% off", "hi": "10% छूट के लिए कोड JHUMKA10 का उपयोग करें"},
    "search_placeholder": {"en": "Search...", "hi": "खोजें..."},
    "my_account": {"en": "My Account", "hi": "मेरा खाता"},
    "stay_in_the_loop": {"en": "Stay in the Loop", "hi": "अपडेट रहें"},
    "newsletter_desc": {"en": "Get jhumka box restock updates and simple festive offers straight to your inbox.", "hi": "झुमका बॉक्स रेस्टॉक अपडेट और सरल उत्सव के ऑफर सीधे अपने इनबॉक्स में प्राप्त करें。"},
    "enter_email": {"en": "Enter your email", "hi": "अपना ईमेल दर्ज करें"},
    "subscribe": {"en": "Subscribe", "hi": "सब्सक्राइब करें"},
    "card": {"en": "Card", "hi": "कार्ड"},
    "upi": {"en": "UPI", "hi": "यूपीआई"},
    "wallet": {"en": "Wallet", "hi": "वॉलेट"},
    "cod": {"en": "COD", "hi": "कैश ऑन डिलीवरी"},
    "best_sellers": {"en": "Best Sellers", "hi": "सबसे ज़्यादा बिकने वाले"},
    "view_all": {"en": "View All Collection", "hi": "सभी संग्रह देखें"},
    "new_arrivals": {"en": "New Arrivals", "hi": "नये उत्पाद"},
    "flash_sale": {"en": "Flash Sale", "hi": "फ्लैश सेल"},
    "atelier_title": {"en": "The Soul of the Atelier", "hi": "कार्यशाला की आत्मा"},
    "filter_category": {"en": "Filter by Category", "hi": "श्रेणी द्वारा फ़िल्टर करें"},
    "filter_brand": {"en": "Filter by Brand", "hi": "ब्रांड द्वारा फ़िल्टर करें"},
    "sort_by": {"en": "Sort By", "hi": "क्रमबद्ध करें"},
    "price_range": {"en": "Price Range", "hi": "मूल्य सीमा"},
    "apply_filters": {"en": "Apply Filters", "hi": "फ़िल्टर लागू करें"},
    "clear_all": {"en": "Clear All", "hi": "सभी साफ़ करें"},
    "no_products": {"en": "No products found.", "hi": "कोई उत्पाद नहीं मिला。"},
    "reviews": {"en": "Reviews", "hi": "समीक्षाएं"},
    "description": {"en": "Description", "hi": "विवरण"},
    "similar_products": {"en": "Similar Products", "hi": "समान उत्पाद"},
    "write_review": {"en": "Write a Review", "hi": "समीक्षा लिखें"},
    "proceed_to_checkout": {"en": "Proceed to Checkout", "hi": "चेकआउट के लिए आगे बढ़ें"},
    "product": {"en": "Product", "hi": "उत्पाद"},
    "quantity": {"en": "Quantity", "hi": "मात्रा"},
    "subtotal": {"en": "Subtotal", "hi": "उप-कुल"},
    "grand_total": {"en": "Grand Total", "hi": "कुल योग"},
    "filters": {"en": "Filters", "hi": "फ़िल्टर"},
    "category": {"en": "Category", "hi": "श्रेणी"},
    "customer_favorites": {"en": "Customer Favorites", "hi": "ग्राहकों की पसंद"},
    "quick_view": {"en": "Quick View", "hi": "त्वरित दृश्य"},
    "atelier_desc": {"en": "Behind every piece lies a story of heritage, precision, and passion. Our master artisans breathe life into raw materials, creating timeless heirlooms.", "hi": "हर टुकड़े के पीछे विरासत, सटीकता और जुनून की कहानी होती है। हमारे कुशल कारीगर कच्चे माल में जान फूंककर, कालातीत विरासत बनाते हैं。"},
    "unrivaled_craft": {"en": "Unrivaled Craft", "hi": "बेजोड़ शिल्प"},
    "unrivaled_craft_desc": {"en": "Every stone is hand-selected for its fire and brilliance.", "hi": "हर पत्थर को उसकी चमक और आभा के लिए हाथ से चुना जाता है。"},
    "ancestral_techniques": {"en": "Ancestral Techniques", "hi": "पैतृक तकनीकें"},
    "ancestral_desc": {"en": "Reviving lost arts passed down through generations.", "hi": "पीढ़ियों से चली आ रही खोई हुई कलाओं को पुनर्जीवित करना。"},
    "copyright_text": {"en": 'Copyright 2026 HYPEHAVENHUB. All Rights Reserved. Made with <span class="material-symbols-outlined" style="font-size: 16px; vertical-align: middle; color: var(--primary);">favorite</span> for jhumka lovers.', "hi": 'कॉपीराइट 2026 HYPEHAVENHUB. सर्वाधिकार सुरक्षित। झुमका प्रेमियों के लिए <span class="material-symbols-outlined" style="font-size: 16px; vertical-align: middle; color: var(--primary);">favorite</span> के साथ बनाया गया。'},
    "hi_user": {"en": "Hi, ", "hi": "नमस्ते, "}
}


def translate(request, key):
    """Return the UI string for `key` in the currently selected session language."""
    lang = request.session.get('django_language', 'en')
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get('en') or key
