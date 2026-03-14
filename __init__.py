"""
BotForge Network Drive
SMB/Network Drive plugin สำหรับ BotForge
"""

from .plugin import NetworkDrivePlugin
from .smb_client import SMBClient
from .connection_manager import ConnectionManager

__version__ = "1.0.0"
__plugin_name__ = "botforge-network-drive"
__plugin_description__ = "SMB/Network Drive access for BotForge"
__all__ = [
    "NetworkDrivePlugin",
    "SMBClient",
    "ConnectionManager",
]
