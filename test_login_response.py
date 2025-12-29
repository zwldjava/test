import requests
import json

base_url = "https://growth-dev.zhijianai.cc"

login_data = {
    "phone": "18821371697",
    "password": "Ww12345678.."
}

response = requests.post(f"{base_url}/api/auth/login", json=login_data)

print(f"状态码: {response.status_code}")
print(f"响应头: {dict(response.headers)}")
print(f"响应内容:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
