"""
SMB Client - ใช้ pysmb library
"""

import os
from typing import List, Dict, Any, Optional
from smb.SMBConnection import SMBConnection


class SMBClient:
    """Client สำหรับเชื่อมต่อ SMB/CIFS shares"""
    
    def __init__(
        self,
        server: str,
        share: str,
        username: str,
        password: str,
        client_name: str = "BotForge",
        domain: str = "WORKGROUP",
        use_ntlm_v2: bool = True,
        is_direct_tcp: bool = True,
        port: int = 445
    ):
        self.server = server
        self.share = share
        self.username = username
        self.password = password
        self.client_name = client_name
        self.domain = domain
        self.use_ntlm_v2 = use_ntlm_v2
        self.is_direct_tcp = is_direct_tcp
        self.port = port
        self.connection: Optional[SMBConnection] = None
    
    def connect(self) -> bool:
        """เชื่อมต่อ SMB server"""
        try:
            self.connection = SMBConnection(
                self.username,
                self.password,
                self.client_name,
                self.domain,
                use_ntlm_v2=self.use_ntlm_v2,
                is_direct_tcp=self.is_direct_tcp
            )
            
            success = self.connection.connect(
                self.server,
                self.port
            )
            
            return success
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """ตัดการเชื่อมต่อ"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def list_files(self, path: str = "/") -> List[Dict[str, Any]]:
        """ดูรายการไฟล์ในโฟลเดอร์"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            files = self.connection.listPath(self.share, path)
            return [
                {
                    "filename": f.filename,
                    "is_directory": f.isDirectory,
                    "size": f.file_size,
                    "created": f.created_time,
                    "modified": f.last_modified_time,
                    "accessed": f.last_access_time,
                }
                for f in files
                if f.filename not in [".", ".."]
            ]
        except Exception as e:
            print(f"List files error: {e}")
            return []
    
    def read_file(self, remote_path: str, local_path: Optional[str] = None) -> bytes:
        """อ่านไฟล์จาก SMB share"""
        if not self.connection:
            if not self.connect():
                return b""
        
        try:
            if local_path:
                # Download to local file
                with open(local_path, "wb") as f:
                    self.connection.retrieveFile(
                        self.share,
                        remote_path,
                        f
                    )
                with open(local_path, "rb") as f:
                    return f.read()
            else:
                # Read to memory
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp_path = tmp.name
                
                try:
                    self.connection.retrieveFile(
                        self.share,
                        remote_path,
                        open(tmp_path, "wb")
                    )
                    with open(tmp_path, "rb") as f:
                        content = f.read()
                    return content
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                        
        except Exception as e:
            print(f"Read file error: {e}")
            return b""
    
    def write_file(self, remote_path: str, content: bytes):
        """เขียนไฟล์ไปยัง SMB share"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_path = tmp.name
                tmp.write(content)
            
            try:
                with open(tmp_path, "rb") as f:
                    self.connection.storeFile(
                        self.share,
                        remote_path,
                        f
                    )
                return True
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        except Exception as e:
            print(f"Write file error: {e}")
            return False
    
    def delete_file(self, path: str) -> bool:
        """ลบไฟล์"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            self.connection.deleteFiles(self.share, path)
            return True
        except Exception as e:
            print(f"Delete file error: {e}")
            return False
    
    def create_folder(self, path: str) -> bool:
        """สร้างโฟลเดอร์ใหม่"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            self.connection.makeDir(self.share, path)
            return True
        except Exception as e:
            print(f"Create folder error: {e}")
            return False
    
    def delete_folder(self, path: str) -> bool:
        """ลบโฟลเดอร์"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            self.connection.removeDir(self.share, path)
            return True
        except Exception as e:
            print(f"Delete folder error: {e}")
            return False
    
    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """ข้อมูลไฟล์"""
        files = self.list_files(os.path.dirname(path))
        filename = os.path.basename(path)
        
        for f in files:
            if f["filename"] == filename:
                return f
        
        return None
    
    def search(self, pattern: str = "*", path: str = "/") -> List[Dict[str, Any]]:
        """ค้นหาไฟล์"""
        import fnmatch
        files = self.list_files(path)
        
        if pattern == "*":
            return files
        
        return [
            f for f in files
            if fnmatch.fnmatch(f["filename"], pattern)
        ]
