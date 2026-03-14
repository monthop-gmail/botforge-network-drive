"""
BotForge Network Drive - MCP Server
Streamable HTTP transport สำหรับเชื่อมต่อ SMB/Network Drive ผ่าน MCP Protocol
"""

import json
import base64
import sys
import os

# Ensure the parent directory is in sys.path so we can import the package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from smb_client import SMBClient
from connection_manager import ConnectionManager
from plugin import NetworkDrivePlugin

# Initialize the MCP server
mcp = FastMCP("botforge-network-drive")

# Initialize the plugin instance (shared across all tool calls)
plugin = NetworkDrivePlugin()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def drive_add_connection(
    name: str,
    server: str,
    share: str,
    username: str,
    password: str,
    domain: str = "WORKGROUP",
) -> str:
    """เพิ่ม SMB connection ใหม่ไปยัง Network Drive
    สร้างการเชื่อมต่อ SMB/CIFS ไปยังเซิร์ฟเวอร์ที่ระบุ

    Args:
        name: ชื่อ connection สำหรับอ้างอิง
        server: IP หรือ hostname ของ SMB server
        share: ชื่อ share folder
        username: ชื่อผู้ใช้สำหรับเข้าสู่ระบบ
        password: รหัสผ่าน
        domain: โดเมน (ค่าเริ่มต้น WORKGROUP)
    """
    try:
        plugin.add_connection(
            name=name,
            server=server,
            share=share,
            username=username,
            password=password,
            domain=domain,
        )
        return json.dumps(
            {"success": True, "message": f"เพิ่ม connection '{name}' สำเร็จ"},
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e)},
            ensure_ascii=False,
        )


@mcp.tool()
def drive_remove_connection(name: str) -> str:
    """ลบ SMB connection ที่มีอยู่
    ตัดการเชื่อมต่อและลบ connection ออกจากรายการ

    Args:
        name: ชื่อ connection ที่ต้องการลบ
    """
    try:
        result = plugin.remove_connection(name)
        if result:
            return json.dumps(
                {"success": True, "message": f"ลบ connection '{name}' สำเร็จ"},
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {"success": False, "error": f"ไม่พบ connection '{name}'"},
                ensure_ascii=False,
            )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e)},
            ensure_ascii=False,
        )


@mcp.tool()
def drive_list_connections() -> str:
    """แสดงรายการ SMB connections ทั้งหมด
    ดูรายการการเชื่อมต่อที่มีอยู่ พร้อมสถานะการเชื่อมต่อ
    """
    try:
        connections = plugin.list_connections()
        return json.dumps(
            {"success": True, "connections": connections},
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e)},
            ensure_ascii=False,
        )


@mcp.tool()
def drive_list_files(connection: str, path: str = "/") -> str:
    """แสดงรายการไฟล์และโฟลเดอร์ในไดเรกทอรีที่ระบุ
    ดูรายชื่อไฟล์ ขนาด วันที่แก้ไข ในโฟลเดอร์บน Network Drive

    Args:
        connection: ชื่อ connection ที่ต้องการใช้
        path: พาธของโฟลเดอร์ (ค่าเริ่มต้น "/")
    """
    try:
        files = plugin.list_files(connection, path)
        # Convert datetime objects to string for JSON serialization
        serializable_files = _make_serializable(files)
        return json.dumps(
            {"success": True, "path": path, "files": serializable_files},
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e)},
            ensure_ascii=False,
        )


@mcp.tool()
def drive_read_file(connection: str, path: str) -> str:
    """อ่านเนื้อหาไฟล์จาก Network Drive
    อ่านไฟล์และส่งกลับเนื้อหา (ไฟล์ไบนารีจะถูกเข้ารหัส base64)

    Args:
        connection: ชื่อ connection ที่ต้องการใช้
        path: พาธของไฟล์ที่ต้องการอ่าน
    """
    try:
        content = plugin.read_file(connection, path)
        if content == b"":
            return json.dumps(
                {"success": False, "error": f"ไม่สามารถอ่านไฟล์ '{path}' หรือไม่พบ connection"},
                ensure_ascii=False,
            )

        # Try to decode as text first
        try:
            text = content.decode("utf-8")
            return json.dumps(
                {
                    "success": True,
                    "path": path,
                    "encoding": "utf-8",
                    "content": text,
                },
                ensure_ascii=False,
            )
        except UnicodeDecodeError:
            # Binary file - return base64 encoded
            b64 = base64.b64encode(content).decode("ascii")
            return json.dumps(
                {
                    "success": True,
                    "path": path,
                    "encoding": "base64",
                    "content": b64,
                    "size": len(content),
                },
                ensure_ascii=False,
            )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e)},
            ensure_ascii=False,
        )


@mcp.tool()
def drive_write_file(
    connection: str,
    path: str,
    content: str,
    encoding: str = "utf-8",
) -> str:
    """เขียนไฟล์ไปยัง Network Drive
    สร้างหรือเขียนทับไฟล์บน Network Drive (รองรับ base64 สำหรับไฟล์ไบนารี)

    Args:
        connection: ชื่อ connection ที่ต้องการใช้
        path: พาธของไฟล์ที่ต้องการเขียน
        content: เนื้อหาไฟล์ (ข้อความ หรือ base64 string)
        encoding: การเข้ารหัส ("utf-8" หรือ "base64") ค่าเริ่มต้น "utf-8"
    """
    try:
        if encoding == "base64":
            file_bytes = base64.b64decode(content)
        else:
            file_bytes = content.encode(encoding)

        result = plugin.write_file(connection, path, file_bytes)
        if result:
            return json.dumps(
                {"success": True, "message": f"เขียนไฟล์ '{path}' สำเร็จ"},
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {"success": False, "error": f"ไม่สามารถเขียนไฟล์ '{path}'"},
                ensure_ascii=False,
            )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e)},
            ensure_ascii=False,
        )


@mcp.tool()
def drive_delete_file(connection: str, path: str) -> str:
    """ลบไฟล์จาก Network Drive
    ลบไฟล์ที่ระบุออกจาก SMB share

    Args:
        connection: ชื่อ connection ที่ต้องการใช้
        path: พาธของไฟล์ที่ต้องการลบ
    """
    try:
        result = plugin.delete_file(connection, path)
        if result:
            return json.dumps(
                {"success": True, "message": f"ลบไฟล์ '{path}' สำเร็จ"},
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {"success": False, "error": f"ไม่สามารถลบไฟล์ '{path}'"},
                ensure_ascii=False,
            )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e)},
            ensure_ascii=False,
        )


@mcp.tool()
def drive_create_folder(connection: str, path: str) -> str:
    """สร้างโฟลเดอร์ใหม่บน Network Drive
    สร้างไดเรกทอรีใหม่บน SMB share

    Args:
        connection: ชื่อ connection ที่ต้องการใช้
        path: พาธของโฟลเดอร์ที่ต้องการสร้าง
    """
    try:
        result = plugin.create_folder(connection, path)
        if result:
            return json.dumps(
                {"success": True, "message": f"สร้างโฟลเดอร์ '{path}' สำเร็จ"},
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {"success": False, "error": f"ไม่สามารถสร้างโฟลเดอร์ '{path}'"},
                ensure_ascii=False,
            )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e)},
            ensure_ascii=False,
        )


@mcp.tool()
def drive_delete_folder(connection: str, path: str) -> str:
    """ลบโฟลเดอร์จาก Network Drive
    ลบไดเรกทอรีที่ระบุออกจาก SMB share

    Args:
        connection: ชื่อ connection ที่ต้องการใช้
        path: พาธของโฟลเดอร์ที่ต้องการลบ
    """
    try:
        result = plugin.delete_folder(connection, path)
        if result:
            return json.dumps(
                {"success": True, "message": f"ลบโฟลเดอร์ '{path}' สำเร็จ"},
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {"success": False, "error": f"ไม่สามารถลบโฟลเดอร์ '{path}'"},
                ensure_ascii=False,
            )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e)},
            ensure_ascii=False,
        )


@mcp.tool()
def drive_get_file_info(connection: str, path: str) -> str:
    """ดูข้อมูลรายละเอียดของไฟล์บน Network Drive
    แสดงชื่อไฟล์ ขนาด วันที่สร้าง วันที่แก้ไข

    Args:
        connection: ชื่อ connection ที่ต้องการใช้
        path: พาธของไฟล์ที่ต้องการดูข้อมูล
    """
    try:
        info = plugin.get_file_info(connection, path)
        if info:
            serializable_info = _make_serializable(info)
            return json.dumps(
                {"success": True, "path": path, "info": serializable_info},
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {"success": False, "error": f"ไม่พบไฟล์ '{path}'"},
                ensure_ascii=False,
            )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e)},
            ensure_ascii=False,
        )


@mcp.tool()
def drive_search(connection: str, pattern: str, path: str = "/") -> str:
    """ค้นหาไฟล์บน Network Drive
    ค้นหาไฟล์ตาม pattern (เช่น *.pdf, *.docx) ในโฟลเดอร์ที่ระบุ

    Args:
        connection: ชื่อ connection ที่ต้องการใช้
        pattern: รูปแบบการค้นหา เช่น "*.pdf", "report*"
        path: พาธเริ่มต้นสำหรับค้นหา (ค่าเริ่มต้น "/")
    """
    try:
        results = plugin.search(connection, pattern, path)
        serializable_results = _make_serializable(results)
        return json.dumps(
            {
                "success": True,
                "pattern": pattern,
                "path": path,
                "results": serializable_results,
                "count": len(serializable_results),
            },
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e)},
            ensure_ascii=False,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_serializable(obj):
    """Convert objects to JSON-serializable types.

    Handles datetime/float timestamps and other non-serializable types
    returned by pysmb.
    """
    if isinstance(obj, list):
        return [_make_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        # Fall back to string representation
        return str(obj)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=3002)
