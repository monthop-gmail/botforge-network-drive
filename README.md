# BotForge Network Drive

SMB/Network Drive plugin สำหรับ BotForge - เข้าถึง shared folders และ network drives

## Features

- เชื่อมต่อ SMB/CIFS shares
- อ่าน/เขียนไฟล์บน network drive
- ดูรายการไฟล์และโฟลเดอร์
- ค้นหาไฟล์
- Upload/Download ไฟล์
- รองรับ multiple connections

## Installation

```bash
git clone https://github.com/monthop-gmail/botforge-network-drive.git
cd botforge-network-drive
pip install -r requirements.txt
```

## Quick Start

```python
from plugin import NetworkDrivePlugin

# Initialize
drive = NetworkDrivePlugin()

# เพิ่ม connection
drive.add_connection(
    name="office-server",
    server="192.168.1.100",
    share="SharedFolder",
    username="user",
    password="pass"
)

# ดูรายการไฟล์
files = drive.list_files("office-server", "/documents")

# อ่านไฟล์
content = drive.read_file("office-server", "/documents/report.pdf")

# เขียนไฟล์ (รับ bytes)
drive.write_file("office-server", "/documents/new.txt", b"Hello World")

# ค้นหาไฟล์
results = drive.search("office-server", "*.pdf", "/documents")
```

## Usage with LINE Bot

```python
from plugin import NetworkDrivePlugin

drive = NetworkDrivePlugin(bot=line_bot_api)

@drive.register("list")
def handle_list(user_id, params):
    path = params.get("path", "/")
    files = drive.list_files("office-server", path)
    return "\n".join([f['filename'] for f in files])

@drive.register("download")
def handle_download(user_id, params):
    file_path = params.get("file")
    content = drive.read_file("office-server", file_path)
    return f"Downloaded {len(content)} bytes"

# เรียกใช้ command
result = drive.execute_command("list", user_id, {"path": "/documents"})
```

## Supported Protocols

- SMBv1/CIFS, SMBv2, SMBv3
- Windows Shared Folders
- Samba Shares

## Security

- NTLM / NTLMv2 authentication
- SMB Encryption (via pysmb)

## API Reference

| Method | Description |
|--------|-------------|
| `add_connection(name, server, share, username, password, **kwargs)` | เพิ่ม connection ใหม่ |
| `remove_connection(name)` | ลบ connection |
| `list_connections()` | ดูรายการ connections ทั้งหมด |
| `list_files(connection, path)` | ดูรายการไฟล์ในโฟลเดอร์ |
| `read_file(connection, path)` | อ่านไฟล์ (คืน bytes) |
| `write_file(connection, path, content)` | เขียนไฟล์ (รับ bytes) |
| `delete_file(connection, path)` | ลบไฟล์ |
| `create_folder(connection, path)` | สร้างโฟลเดอร์ |
| `delete_folder(connection, path)` | ลบโฟลเดอร์ |
| `search(connection, pattern, path)` | ค้นหาไฟล์ตาม pattern |
| `get_file_info(connection, path)` | ดูข้อมูลไฟล์ |
| `disconnect(name)` | ตัดการเชื่อมต่อ |
| `register(name)` | Decorator สำหรับ register command handler |
| `execute_command(command, user_id, params)` | เรียกใช้ registered command |

## MCP Server (AI Agent Integration)

รองรับ MCP Protocol ผ่าน **Streamable HTTP transport** ให้ AI agent เรียกใช้ network drive ได้โดยตรง

### รัน MCP Server

```bash
python mcp_server.py  # เปิด HTTP server ที่ port 3002
```

### ตั้งค่าฝั่ง AI Agent

```json
{
  "mcpServers": {
    "network-drive": {
      "url": "http://localhost:3002/mcp"
    }
  }
}
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `drive_add_connection` | เพิ่ม SMB connection ใหม่ |
| `drive_remove_connection` | ลบ connection |
| `drive_list_connections` | แสดงรายการ connections ทั้งหมด |
| `drive_list_files` | ดูรายการไฟล์ในโฟลเดอร์ |
| `drive_read_file` | อ่านไฟล์ (text/base64) |
| `drive_write_file` | เขียนไฟล์ (text/base64) |
| `drive_delete_file` | ลบไฟล์ |
| `drive_create_folder` | สร้างโฟลเดอร์ใหม่ |
| `drive_delete_folder` | ลบโฟลเดอร์ |
| `drive_get_file_info` | ดูข้อมูลรายละเอียดไฟล์ |
| `drive_search` | ค้นหาไฟล์ตาม pattern |

## Examples

ดูตัวอย่างเพิ่มเติมใน [examples/](./examples/)

## License

MIT
