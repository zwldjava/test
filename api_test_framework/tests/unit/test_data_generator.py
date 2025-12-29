import pytest

from utils.data_generator import DataGenerator


class TestDataGenerator:

    def test_random_string(self):
        s = DataGenerator.random_string(10)
        assert len(s) == 10
        assert isinstance(s, str)

    def test_random_email(self):
        email = DataGenerator.random_email()
        assert "@" in email
        assert "." in email

    def test_random_phone(self):
        phone = DataGenerator.random_phone()
        assert isinstance(phone, str)

    def test_random_int(self):
        num = DataGenerator.random_int(1, 100)
        assert 1 <= num <= 100
        assert isinstance(num, int)

    def test_random_float(self):
        num = DataGenerator.random_float(0.0, 100.0)
        assert 0.0 <= num <= 100.0
        assert isinstance(num, float)

    def test_generate_user_data(self):
        user_data = DataGenerator.generate_user_data()
        assert "username" in user_data
        assert "email" in user_data
        assert "name" in user_data
        assert isinstance(user_data, dict)

    def test_generate_product_data(self):
        product_data = DataGenerator.generate_product_data()
        assert "name" in product_data
        assert "price" in product_data
        assert "stock" in product_data
        assert isinstance(product_data, dict)

    def test_generate_order_data(self):
        order_data = DataGenerator.generate_order_data()
        assert "order_id" in order_data
        assert "user_id" in order_data
        assert "items" in order_data
        assert isinstance(order_data["items"], list)
