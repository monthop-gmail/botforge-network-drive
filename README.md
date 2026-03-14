# BotForge Network Drive

MCP plugin สำหรับเข้าถึง SMB/Network Drive, shared folders

## Features

- เชื่อมต่อ SMB/CIFS shares (v1/v2/v3)
- อ่าน/เขียนไฟล์บน network drive
- ดูรายการไฟล์และโฟลเดอร์
- ค้นหาไฟล์
- Upload/Download ไฟล์
- รองรับ multiple connections
- NTLM/NTLMv2 authentication

## Installation

```bash
git clone https://github.com/monthop-gmail/botforge-network-drive.git
cd botforge-network-drive
pip install -r requirements.txt
```

## MCP Server (Streamable HTTP)

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
| `drive_add_connection` | เพิ่ม SMB connection (params: name, server, share, username, password, domain) |
| `drive_remove_connection` | ลบ connection (params: name) |
| `drive_list_connections` | แสดงรายการ connections ทั้งหมด |
| `drive_list_files` | ดูรายการไฟล์ในโฟลเดอร์ (params: connection, path) |
| `drive_read_file` | อ่านไฟล์ - text/base64 (params: connection, path) |
| `drive_write_file` | เขียนไฟล์ - text/base64 (params: connection, path, content, encoding) |
| `drive_delete_file` | ลบไฟล์ (params: connection, path) |
| `drive_create_folder` | สร้างโฟลเดอร์ (params: connection, path) |
| `drive_delete_folder` | ลบโฟลเดอร์ (params: connection, path) |
| `drive_get_file_info` | ดูข้อมูลไฟล์ (params: connection, path) |
| `drive_search` | ค้นหาไฟล์ตาม pattern (params: connection, pattern, path) |

## License

MIT
