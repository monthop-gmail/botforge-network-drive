"""
Example: LINE Bot integration with Network Drive
"""

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage
from plugin import NetworkDrivePlugin

# LINE Bot configuration
line_bot_api = LineBotApi("YOUR_CHANNEL_ACCESS_TOKEN")
handler = WebhookHandler("YOUR_CHANNEL_SECRET")

# Initialize plugin
drive = NetworkDrivePlugin(line_bot_api)

# Add SMB connection
drive.add_connection(
    name="office",
    server="192.168.1.100",
    share="SharedFolder",
    username="user",
    password="password"
)

# Register commands
@drive.register("list")
def handle_list(user_id, params):
    """List files in directory"""
    path = params.get("path", "/")
    files = drive.list_files("office", path)
    
    if not files:
        return "📂 โฟลเดอร์ว่างเปล่า"
    
    lines = [f"📁 {path}"]
    for f in files[:20]:  # Show max 20 files
        icon = "📁" if f["is_directory"] else "📄"
        lines.append(f"{icon} {f['filename']}")
    
    return "\n".join(lines)

@drive.register("download")
def handle_download(user_id, params):
    """Download file"""
    file_path = params.get("file")
    if not file_path:
        return "❌ กรุณาระบุไฟล์"
    
    content = drive.read_file("office", file_path)
    
    # Send file to user (implement based on file type)
    # For now, just return success message
    return f"✅ ดาวน์โหลดเสร็จแล้ว: {file_path}"

@drive.register("upload")
def handle_upload(user_id, params):
    """Upload file"""
    file_data = params.get("file_data")
    dest_path = params.get("path")
    
    if not file_data or not dest_path:
        return "❌ ข้อมูลไม่ครบ"
    
    success = drive.write_file("office", dest_path, file_data)
    
    if success:
        return f"✅ อัพโหลดเสร็จแล้ว: {dest_path}"
    else:
        return "❌ อัพโหลดล้มเหลว"

@drive.register("search")
def handle_search(user_id, params):
    """Search files"""
    pattern = params.get("pattern", "*")
    path = params.get("path", "/")
    
    results = drive.search("office", pattern, path)
    
    if not results:
        return f"🔍 ไม่พบไฟล์ที่ตรงกับ: {pattern}"
    
    lines = [f"🔍 ผลการค้นหา: {pattern}"]
    for f in results[:20]:
        icon = "📁" if f["is_directory"] else "📄"
        lines.append(f"{icon} {f['filename']}")
    
    return "\n".join(lines)

# Webhook handler
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_id = event.source.user_id
    text = event.message.text
    
    # Parse command
    if text.startswith("/drive"):
        parts = text.split()
        command = parts[1] if len(parts) > 1 else "list"
        params = {}
        
        if command == "list" and len(parts) > 2:
            params["path"] = parts[2]
        elif command == "download" and len(parts) > 2:
            params["file"] = parts[2]
        elif command == "search" and len(parts) > 2:
            params["pattern"] = parts[2]
        
        # Execute command
        result = drive.execute_command(command, user_id, params)
        
        line_bot_api.reply_message(event.reply_token, result)
        return
    
    # Default response
    line_bot_api.reply_message(
        event.reply_token,
        "คำสั่งที่ใช้ได้:\n"
        "/drive list [path] - ดูรายการไฟล์\n"
        "/drive download <file> - ดาวน์โหลดไฟล์\n"
        "/drive search <pattern> - ค้นหาไฟล์\n"
        "/drive upload - อัพโหลดไฟล์"
    )

if __name__ == "__main__":
    from flask import Flask, request, abort
    
    app = Flask(__name__)
    
    @app.route("/callback", methods=["POST"])
    def callback():
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)
        
        try:
            handler.handle(body, signature)
        except:
            abort(400)
        
        return "OK"
    
    app.run(port=8000)
