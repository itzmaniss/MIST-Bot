import httpx
from typing import Dict, Any

class ServerManager:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
    
    async def send_api_request(self, endpoint: str, params: Dict[str, Any]) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            return await client.get(url=f"{self.api_url}/{endpoint}", params=params)
    
    async def start_server(self, instance_id: str, daemon_id: str) -> httpx.Response:
        params = {
            "apikey": self.api_key,
            "uuid": instance_id,
            "daemonId": daemon_id
        }
        return await self.send_api_request("protected_instance/open", params)
    
    async def stop_server(self, instance_id: str, daemon_id: str) -> httpx.Response:
        params = {
            "apikey": self.api_key,
            "uuid": instance_id,
            "daemonId": daemon_id
        }
        return await self.send_api_request("protected_instance/stop", params)

