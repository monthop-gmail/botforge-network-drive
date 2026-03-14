# BotForge Network Drive

SMB/Network Drive plugin สำหรับ BotForge - เข้าถึง shared folders และ network drives

## Features

- ✅ เชื่อมต่อ SMB/CIFS shares
- ✅ อ่าน/เขียนไฟล์บน network drive
- ✅ ดูรายการไฟล์และโฟลเดอร์
- ✅ ค้นหาไฟล์
- ✅ Upload/Download ไฟล์
- ✅ Progress tracking สำหรับไฟล์ใหญ่
- ✅ รองรับ multiple connections

## Installation

```bash
pip install botforge-network-drive
```

## Quick Start

```python
from botforge_network_drive import NetworkDrivePlugin

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

# เขียนไฟล์
drive.write_file("office-server", "/documents/new.txt", "Hello World")

# ค้นหาไฟล์
results = drive.search("office-server", "*.pdf", "/documents")
```

## Usage with LINE Bot

```python
from botforge_network_drive import NetworkDrivePlugin

drive = NetworkDrivePlugin(bot)

@drive.command("list")
def handle_list(user_id, params):
    """List files in directory"""
    path = params.get("path", "/")
    files = drive.list_files("office-server", path)
    return format_file_list(files)

@drive.command("download")
def handle_download(user_id, params):
    """Download file from network drive"""
    file_path = params.get("file")
    content = drive.read_file("office-server", file_path)
    return send_file_to_user(user_id, content)

@drive.command("upload")
def handle_upload(user_id, params):
    """Upload file to network drive"""
    file_data = params.get("file")
    dest_path = params.get("path")
    drive.write_file("office-server", dest_path, file_data)
    return "✅ อัพโหลดเสร็จแล้ว"
```

## Supported Protocols

- SMBv1/CIFS
- SMBv2
- SMBv3
- Windows Shared Folders
- Samba Shares

## Security

- ✅ NTLM authentication
- ✅ NTLMv2 authentication
- ✅ SMB Encryption
- ✅ Credential storage (encrypted)
- ✅ Access control lists

## API Reference

### NetworkDrivePlugin

| Method | Description |
|--------|-------------|
| `add_connection(name, server, share, ...)` | เพิ่ม connection ใหม่ |
| `list_files(connection, path)` | ดูรายการไฟล์ในโฟลเดอร์ |
| `read_file(connection, path)` | อ่านไฟล์ |
| `write_file(connection, path, content)` | เขียนไฟล์ |
| `delete_file(connection, path)` | ลบไฟล์ |
| `create_folder(connection, path)` | สร้างโฟลเดอร์ใหม่ |
| `search(connection, pattern, path)` | ค้นหาไฟล์ |
| `get_file_info(connection, path)` | ข้อมูลไฟล์ (size, modified, etc.) |

## Configuration

```yaml
connections:
  - name: "office-server"
    server: "192.168.1.100"
    share: "SharedFolder"
    username: "user"
    password: "${ENV_VAR}"
    domain: "WORKGROUP"
    
  - name: "nas-drive"
    server: "nas.local"
    share: "Public"
    username: "admin"
    password: "${NAS_PASSWORD}"
```

## Examples

ดูตัวอย่างเพิ่มเติมใน [examples/](./examples/)

## License

MIT
