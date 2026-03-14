"""
Example: Basic usage of BotForge Network Drive
"""

from plugin import NetworkDrivePlugin

# Initialize
drive = NetworkDrivePlugin()

# Add connection
drive.add_connection(
    name="office-server",
    server="192.168.1.100",
    share="SharedFolder",
    username="user",
    password="password123"
)

# List connections
connections = drive.list_connections()
print(f"Connections: {connections}")

# List files
print("\n=== List Files ===")
files = drive.list_files("office-server", "/documents")
for f in files:
    print(f"  {f['filename']} ({f['size']} bytes)")

# Read file
print("\n=== Read File ===")
content = drive.read_file("office-server", "/documents/report.txt")
print(f"Content: {content.decode('utf-8')}")

# Write file
print("\n=== Write File ===")
success = drive.write_file(
    "office-server",
    "/documents/new_file.txt",
    b"Hello from BotForge!"
)
print(f"Write success: {success}")

# Search files
print("\n=== Search Files ===")
results = drive.search("office-server", "*.txt", "/documents")
for f in results:
    print(f"  {f['filename']}")

# Get file info
print("\n=== File Info ===")
info = drive.get_file_info("office-server", "/documents/report.txt")
if info:
    print(f"  Name: {info['filename']}")
    print(f"  Size: {info['size']} bytes")
    print(f"  Modified: {info['modified']}")

# Create folder
print("\n=== Create Folder ===")
success = drive.create_folder("office-server", "/documents/new_folder")
print(f"Create folder success: {success}")

# Disconnect
drive.disconnect()
print("\nDisconnected!")
