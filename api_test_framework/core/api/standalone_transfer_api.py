from typing import Dict, Optional
from core.api.base_api import BaseAPI


class StandaloneTransferAPI(BaseAPI):
    def __init__(self, client=None, context=None):
        super().__init__(client, context)
        self.base_endpoint = "/standalone-transfer"
    
    def get_transfer_list(
        self,
        page: int = 1,
        page_size: int = 10,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        params = {
            "page": page,
            "page_size": page_size
        }
        
        if start_time is not None:
            params["start_time"] = start_time
        
        if end_time is not None:
            params["end_time"] = end_time
        
        return self._request(
            method="GET",
            endpoint=self.base_endpoint,
            params=params,
            headers=headers
        )
    
    def create_transfer(
        self,
        actual_payment_amount: int,
        final_payment_amount: int,
        payment_account_id: int,
        payment_method: int,
        platform: str,
        platform_account: str,
        platform_order_sn: str,
        receipt_account_name: str,
        receipt_account_number: str,
        shop_id: int,
        headers: Optional[Dict[str, str]] = None
    ):
        transfer_data = {
            "actual_payment_amount": actual_payment_amount,
            "final_payment_amount": final_payment_amount,
            "payment_account_id": payment_account_id,
            "payment_method": payment_method,
            "platform": platform,
            "platform_account": platform_account,
            "platform_order_sn": platform_order_sn,
            "receipt_account_name": receipt_account_name,
            "receipt_account_number": receipt_account_number,
            "shop_id": shop_id
        }
        
        return self._request(
            method="POST",
            endpoint=self.base_endpoint,
            json=transfer_data,
            headers=headers
        )
