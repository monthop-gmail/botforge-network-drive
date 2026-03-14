"""
Connection Manager - จัดการ multiple SMB connections
"""

from typing import Dict, List, Optional, Any
from .smb_client import SMBClient


class ConnectionManager:
    """จัดการ multiple SMB connections"""
    
    def __init__(self):
        self.connections: Dict[str, SMBClient] = {}
        self.default_connection: Optional[str] = None
    
    def add_connection(
        self,
        name: str,
        server: str,
        share: str,
        username: str,
        password: str,
        **kwargs
    ) -> SMBClient:
        """เพิ่ม connection ใหม่"""
        client = SMBClient(
            server=server,
            share=share,
            username=username,
            password=password,
            **kwargs
        )
        
        self.connections[name] = client
        
        if not self.default_connection:
            self.default_connection = name
        
        return client
    
    def remove_connection(self, name: str) -> bool:
        """ลบ connection"""
        if name in self.connections:
            self.connections[name].disconnect()
            del self.connections[name]
            return True
        return False
    
    def get_connection(self, name: Optional[str] = None) -> Optional[SMBClient]:
        """ดึง connection"""
        conn_name = name or self.default_connection
        
        if not conn_name:
            return None
        
        return self.connections.get(conn_name)
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """รายการ connections ทั้งหมด"""
        return [
            {
                "name": name,
                "server": client.server,
                "share": client.share,
                "connected": client.connection is not None
            }
            for name, client in self.connections.items()
        ]
    
    def disconnect_all(self):
        """ตัดการเชื่อมต่อทั้งหมด"""
        for client in self.connections.values():
            client.disconnect()
