from typing import Dict, Optional
import requests
from core.api.base_api import BaseAPI


class UserAPI(BaseAPI):
    def get_profile(self) -> requests.Response:
        response = self._request("GET", "/user/profile")
        return response
    
    def get_profile_and_extract(self) -> Optional[Dict]:
        response = self.get_profile()
        if response.status_code == 200:
            return self._extract_data(response)
        return None
    
    def update_profile(self, data: Dict) -> requests.Response:
        response = self._request("PUT", "/user/profile", json=data)
        return response
    
    def change_password(self, old_password: str, new_password: str) -> requests.Response:
        response = self._request(
            "POST",
            "/user/change-password",
            json={
                "oldPassword": old_password,
                "newPassword": new_password
            }
        )
        return response
    
    def get_user_list(self, page: int = 1, page_size: int = 10) -> requests.Response:
        response = self._request(
            "GET",
            "/user/list",
            params={"page": page, "pageSize": page_size}
        )
        return response
    
    def delete_user(self, user_id: int) -> requests.Response:
        response = self._request("DELETE", f"/user/{user_id}")
        return response
    
    def get_user_by_id(self, user_id: int) -> requests.Response:
        response = self._request("GET", f"/user/{user_id}")
        return response
