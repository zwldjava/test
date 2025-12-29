import json
import random
import string
from typing import Any, Dict, List

from faker import Faker

from utils.logger import get_logger

fake = Faker("zh_CN")
logger = get_logger(__name__)


class DataGenerator:
    @staticmethod
    def random_string(length: int = 10) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def random_email() -> str:
        return str(fake.email())

    @staticmethod
    def random_phone() -> str:
        return str(fake.phone_number())

    @staticmethod
    def random_name() -> str:
        return str(fake.name())

    @staticmethod
    def random_address() -> str:
        return str(fake.address())

    @staticmethod
    def random_int(min_val: int = 1, max_val: int = 100) -> int:
        return random.randint(min_val, max_val)

    @staticmethod
    def random_float(
        min_val: float = 0.0, max_val: float = 100.0, decimals: int = 2
    ) -> float:
        return round(random.uniform(min_val, max_val), decimals)

    @staticmethod
    def random_date(start_year: int = 2020, end_year: int = 2025) -> str:
        return str(
            fake.date_between(
                start_date=f"{start_year}-01-01", end_date=f"{end_year}-12-31"
            ).strftime("%Y-%m-%d")
        )

    @staticmethod
    def random_uuid() -> str:
        return str(fake.uuid4())

    @staticmethod
    def random_url() -> str:
        return str(fake.url())

    @staticmethod
    def random_ip() -> str:
        return str(fake.ipv4())

    @staticmethod
    def random_user_agent() -> str:
        return str(fake.user_agent())

    @staticmethod
    def generate_user_data() -> Dict[str, Any]:
        return {
            "username": fake.user_name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "name": fake.name(),
            "age": random.randint(18, 60),
            "address": fake.address(),
            "avatar": fake.image_url(),
        }

    @staticmethod
    def generate_product_data() -> Dict[str, Any]:
        return {
            "name": fake.sentence(nb_words=3),
            "description": fake.text(max_nb_chars=200),
            "price": round(random.uniform(10.0, 1000.0), 2),
            "stock": random.randint(0, 100),
            "category": fake.word(),
            "sku": f"SKU-{fake.uuid4()[:8].upper()}",
            "active": random.choice([True, False]),
        }

    @staticmethod
    def generate_order_data() -> Dict[str, Any]:
        return {
            "order_id": fake.uuid4(),
            "user_id": fake.uuid4(),
            "items": [
                {
                    "product_id": fake.uuid4(),
                    "quantity": random.randint(1, 5),
                    "price": round(random.uniform(10.0, 100.0), 2),
                }
                for _ in range(random.randint(1, 5))
            ],
            "total_amount": round(random.uniform(50.0, 500.0), 2),
            "status": random.choice(
                ["pending", "paid", "shipped", "delivered", "cancelled"]
            ),
            "shipping_address": fake.address(),
        }

    @staticmethod
    def load_test_data(file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return list(data) if isinstance(data, list) else []
        except FileNotFoundError:
            logger.error(f"测试数据文件不存在: {file_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"测试数据文件格式错误: {e}")
            return []

    @staticmethod
    def save_test_data(data: Any, file_path: str):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"测试数据已保存: {file_path}")
        except Exception as e:
            logger.error(f"保存测试数据失败: {e}")
