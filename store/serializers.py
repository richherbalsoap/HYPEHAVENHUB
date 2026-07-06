from rest_framework import serializers
from .models import Category, Product, ProductVariant

class CategorySerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')
    body_html = serializers.SerializerMethodField()
    handle = serializers.CharField(source='slug')
    image = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'body_html', 'handle', 'image', 'created_at', 'updated_at']

    def get_body_html(self, obj):
        return f"<p>{obj.description}</p>"

    def get_image(self, obj):
        host_uri = self.context.get('host_uri', '')
        image_url = obj.display_image_url
        if image_url and not image_url.startswith('http'):
            image_url = host_uri + image_url
        return {"src": image_url} if image_url else None

    def get_created_at(self, obj):
        if hasattr(obj, 'created_at') and obj.created_at:
            return obj.created_at.isoformat()
        return "2026-07-04T00:00:00Z"

    def get_updated_at(self, obj):
        return self.get_created_at(obj)


class ProductVariantSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='label')
    price = serializers.SerializerMethodField()
    compare_at_price = serializers.SerializerMethodField()
    quantity = serializers.IntegerField(source='stock')
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    taxable = serializers.SerializerMethodField()
    option_values = serializers.SerializerMethodField()
    grams = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    weight = serializers.SerializerMethodField()
    weight_unit = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'title', 'price', 'compare_at_price', 'sku', 'quantity', 
            'created_at', 'updated_at', 'taxable', 'option_values', 
            'grams', 'image', 'weight', 'weight_unit'
        ]

    def get_price(self, obj):
        selling_price = float(obj.product.selling_price) + float(obj.additional_price)
        return f"{selling_price:.2f}"

    def get_compare_at_price(self, obj):
        compare_at_price = float(obj.product.base_price) + float(obj.additional_price)
        return f"{compare_at_price:.2f}"

    def get_created_at(self, obj):
        if hasattr(obj, 'created_at') and obj.created_at:
            return obj.created_at.isoformat()
        return obj.product.created_at.isoformat()

    def get_updated_at(self, obj):
        return obj.product.updated_at.isoformat()

    def get_taxable(self, obj):
        return True

    def get_option_values(self, obj):
        return {
            "Shade": obj.shade_name or "Default",
            "Size": obj.size or "Default",
            "Finish": obj.finish or "Default"
        }

    def get_grams(self, obj):
        return 500

    def get_weight(self, obj):
        return 0.5

    def get_weight_unit(self, obj):
        return "kg"

    def get_image(self, obj):
        host_uri = self.context.get('host_uri', '')
        variant_image_url = ""
        if obj.image:
            variant_image_url = host_uri + obj.image.url
        elif obj.product.display_image_url:
            variant_image_url = obj.product.display_image_url
            if not variant_image_url.startswith('http'):
                variant_image_url = host_uri + variant_image_url
        return {"src": variant_image_url} if variant_image_url else None


class ProductSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')
    body_html = serializers.SerializerMethodField()
    vendor = serializers.SerializerMethodField()
    product_type = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    handle = serializers.CharField(source='slug')
    updated_at = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'body_html', 'vendor', 'product_type', 'created_at',
            'handle', 'updated_at', 'tags', 'status', 'variants', 'image', 'options'
        ]

    def get_body_html(self, obj):
        return f"<p>{obj.description}</p>"

    def get_vendor(self, obj):
        return obj.brand.name if obj.brand else "HypeHaven"

    def get_product_type(self, obj):
        return obj.category.name if obj.category else "Jewelry"

    def get_created_at(self, obj):
        return obj.created_at.isoformat()

    def get_updated_at(self, obj):
        return obj.updated_at.isoformat()

    def get_tags(self, obj):
        return obj.category.name if obj.category else ""

    def get_status(self, obj):
        return "active" if obj.is_active else "archived"

    def get_variants(self, obj):
        host_uri = self.context.get('host_uri', '')
        variants = obj.variants.all()
        return ProductVariantSerializer(variants, many=True, context={'host_uri': host_uri}).data

    def get_image(self, obj):
        host_uri = self.context.get('host_uri', '')
        product_image_url = obj.display_image_url
        if product_image_url and not product_image_url.startswith('http'):
            product_image_url = host_uri + product_image_url
        return {"src": product_image_url} if product_image_url else None

    def get_options(self, obj):
        options_list = []
        variants = list(obj.variants.all())
        
        shades = sorted(list({v.shade_name for v in variants if v.shade_name}))
        if shades:
            options_list.append({"name": "Shade", "values": shades})
            
        sizes = sorted(list({v.size for v in variants if v.size}))
        if sizes:
            options_list.append({"name": "Size", "values": sizes})
            
        finishes = sorted(list({v.finish for v in variants if v.finish}))
        if finishes:
            options_list.append({"name": "Finish", "values": finishes})

        if not options_list and variants:
            options_list.append({"name": "Title", "values": ["Default"]})

        return options_list
