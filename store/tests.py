from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Product, ProductVariant

class AdminProductVideoDeleteTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a staff user
        self.admin_user = User.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True,
            is_superuser=True
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            base_price=10.00,
            video_url='https://example.com/test-video.mp4'
        )

    def test_delete_video_unauthenticated(self):
        url = reverse('admin_product_delete_video', args=[self.product.pk])
        response = self.client.post(url)
        # Should redirect to custom admin login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('admin/login/', response.url)

    def test_delete_video_authenticated(self):
        # Authenticate staff user
        self.client.login(email='admin@example.com', password='adminpassword')
        url = reverse('admin_product_delete_video', args=[self.product.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify video_url is empty in the database
        self.product.refresh_from_db()
        self.assertEqual(self.product.video_url, '')


class AdminProductVariantTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin_var@example.com',
            email='admin_var@example.com',
            password='adminpassword',
            is_staff=True,
            is_superuser=True
        )
        self.product = Product.objects.create(
            name='Test Earring Product',
            description='Beautiful artificial jewellery earrings',
            base_price=299.00
        )

    def test_create_and_delete_variant(self):
        self.client.login(email='admin_var@example.com', password='adminpassword')
        
        # Create a variant directly
        variant = ProductVariant.objects.create(
            product=self.product,
            shade_name='Pink, Multicolor',
            additional_price=20.00,
            stock=15,
            image_url='https://example.com/pink-earring.jpg'
        )
        
        self.assertEqual(variant.shade_name, 'Pink, Multicolor')
        self.assertEqual(variant.display_image_url, 'https://example.com/pink-earring.jpg')
        
        # Test AJAX delete endpoint
        url = reverse('admin_variant_delete', args=[variant.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertFalse(ProductVariant.objects.filter(pk=variant.pk).exists())


