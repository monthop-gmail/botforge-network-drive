"""
Main Plugin Interface
"""

from typing import Any, Dict, List, Optional
from .smb_client import SMBClient
from .connection_manager import ConnectionManager


class NetworkDrivePlugin:
    """
    BotForge Network Drive Plugin
    
    Usage:
        drive = NetworkDrivePlugin()
        
        # Add connection
        drive.add_connection(
            name="office",
            server="192.168.1.100",
            share="SharedFolder",
            username="user",
            password="pass"
        )
        
        # List files
        files = drive.list_files("office", "/documents")
        
        # Read file
        content = drive.read_file("office", "/documents/report.pdf")
    """
    
    def __init__(self, bot=None):
        """
        Initialize plugin
        
        Args:
            bot: LINE Bot API object (optional)
        """
        self.bot = bot
        self.manager = ConnectionManager()
        self.commands = {}
    
    def register(self, name: str):
        """
        Register command handler
        
        Usage:
            @drive.register("list_files")
            def handle_list(user_id, params):
                files = drive.list_files("office", params.get("path", "/"))
                return format_file_list(files)
        """
        def decorator(func):
            self.commands[name] = func
            return func
        return decorator
    
    def add_connection(
        self,
        name: str,
        server: str,
        share: str,
        username: str,
        password: str,
        **kwargs
    ) -> SMBClient:
        """
        เพิ่ม SMB connection ใหม่
        
        Args:
            name: Connection name
            server: Server IP or hostname
            share: Share name
            username: Username
            password: Password
            **kwargs: Additional options (domain, port, etc.)
        
        Returns:
            SMBClient instance
        """
        return self.manager.add_connection(
            name=name,
            server=server,
            share=share,
            username=username,
            password=password,
            **kwargs
        )
    
    def remove_connection(self, name: str) -> bool:
        """ลบ connection"""
        return self.manager.remove_connection(name)
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """รายการ connections ทั้งหมด"""
        return self.manager.list_connections()
    
    def get_connection(self, name: Optional[str] = None) -> Optional[SMBClient]:
        """ดึง connection"""
        return self.manager.get_connection(name)
    
    def list_files(self, connection: str, path: str = "/") -> List[Dict[str, Any]]:
        """
        ดูรายการไฟล์ในโฟลเดอร์
        
        Args:
            connection: Connection name
            path: Remote path
        
        Returns:
            List of file info dicts
        """
        client = self.manager.get_connection(connection)
        if not client:
            return []
        
        return client.list_files(path)
    
    def read_file(self, connection: str, path: str, local_path: Optional[str] = None) -> bytes:
        """
        อ่านไฟล์จาก SMB share
        
        Args:
            connection: Connection name
            path: Remote file path
            local_path: Local path to save (optional)
        
        Returns:
            File content as bytes
        """
        client = self.manager.get_connection(connection)
        if not client:
            return b""
        
        return client.read_file(path, local_path)
    
    def write_file(self, connection: str, path: str, content: bytes) -> bool:
        """
        เขียนไฟล์ไปยัง SMB share
        
        Args:
            connection: Connection name
            path: Remote file path
            content: File content
        
        Returns:
            True if successful
        """
        client = self.manager.get_connection(connection)
        if not client:
            return False
        
        return client.write_file(path, content)
    
    def delete_file(self, connection: str, path: str) -> bool:
        """ลบไฟล์"""
        client = self.manager.get_connection(connection)
        if not client:
            return False
        
        return client.delete_file(path)
    
    def create_folder(self, connection: str, path: str) -> bool:
        """สร้างโฟลเดอร์ใหม่"""
        client = self.manager.get_connection(connection)
        if not client:
            return False
        
        return client.create_folder(path)
    
    def delete_folder(self, connection: str, path: str) -> bool:
        """ลบโฟลเดอร์"""
        client = self.manager.get_connection(connection)
        if not client:
            return False
        
        return client.delete_folder(path)
    
    def get_file_info(self, connection: str, path: str) -> Optional[Dict[str, Any]]:
        """ข้อมูลไฟล์"""
        client = self.manager.get_connection(connection)
        if not client:
            return None
        
        return client.get_file_info(path)
    
    def search(self, connection: str, pattern: str, path: str = "/") -> List[Dict[str, Any]]:
        """
        ค้นหาไฟล์
        
        Args:
            connection: Connection name
            pattern: File pattern (e.g., "*.pdf")
            path: Search path
        
        Returns:
            List of matching files
        """
        client = self.manager.get_connection(connection)
        if not client:
            return []
        
        return client.search(pattern, path)
    
    def disconnect(self, name: Optional[str] = None):
        """ตัดการเชื่อมต่อ"""
        if name:
            client = self.manager.get_connection(name)
            if client:
                client.disconnect()
        else:
            self.manager.disconnect_all()
    
    def execute_command(self, command: str, user_id: str, params: Dict[str, Any]):
        """Execute registered command"""
        handler = self.commands.get(command)
        if not handler:
            return f"Unknown command: {command}"
        
        return handler(user_id, params)
