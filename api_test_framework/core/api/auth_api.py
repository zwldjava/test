from typing import Dict, Optional
import requests
from core.api.base_api import BaseAPI


class AuthAPI(BaseAPI):
    def login(self, phone: str, password: str) -> requests.Response:
        response = self._request(
            "POST",
            "/auth/login",
            json={"phone": phone, "password": password}
        )
        return response
    
    def login_and_extract_token(self, phone: str, password: str) -> Optional[str]:
        response = self.login(phone, password)
        if response.status_code == 200:
            return self._extract_token(response)
        return None
    
    def logout(self) -> requests.Response:
        response = self._request("POST", "/auth/logout")
        if response.status_code == 200:
            self.context.remove("token")
        return response
    
    def register(self, phone: str, password: str, confirm_password: str, verification_code: str) -> requests.Response:
        response = self._request(
            "POST",
            "/auth/register",
            json={
                "phone": phone,
                "password": password,
                "confirmPassword": confirm_password,
                "verificationCode": verification_code
            }
        )
        return response
    
    def send_verification_code(self, phone: str) -> requests.Response:
        response = self._request(
            "POST",
            "/auth/send-code",
            json={"phone": phone}
        )
        return response
    
    def reset_password(self, phone: str, new_password: str, verification_code: str) -> requests.Response:
        response = self._request(
            "POST",
            "/auth/reset-password",
            json={
                "phone": phone,
                "newPassword": new_password,
                "verificationCode": verification_code
            }
        )
        return response
    
    def refresh_token(self) -> requests.Response:
        response = self._request("POST", "/auth/refresh-token")
        if response.status_code == 200:
            self._extract_token(response)
        return response
