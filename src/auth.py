import os
import glob
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
import qrcode
import io

# Load env variables for API credentials
load_dotenv()
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

SESSIONS_DIR = "sessions"

if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

def get_available_sessions():
    """Finds all .session files in the sessions/ directory"""
    return glob.glob(f"{SESSIONS_DIR}/*.session")

async def login_with_phone():
    """Login process using phone number and OTP."""
    if not API_ID or not API_HASH:
        print("Error: API_ID or API_HASH not found in .env.")
        return None

    phone = input("Enter your phone number (with country code, e.g., +1...): ").strip()
    if not phone:
        print("Phone number cannot be empty.")
        return None

    session_file_name = os.path.join(SESSIONS_DIR, f"{phone}.session")
    
    # Init client with empty StringSession since it's a new login
    client = TelegramClient(StringSession(""), API_ID, API_HASH)
    
    print("Connecting to Telegram server...")
    # 'start' prompts for OTP automatically via terminal. 
    # If 2FA is enabled, it will also prompt for the password.
    import getpass
    await client.start(
        phone=phone,
        password=lambda: getpass.getpass("This account is protected by 2FA. Enter your Cloud Password: ")
    )
    
    # If successful, save session to file
    new_session_string = client.session.save()
    with open(session_file_name, 'w') as f:
        f.write(new_session_string)
        
    print(f"\nLogin Successful! Session saved as '{session_file_name}'.")
    return client

async def login_with_qr():
    """Login process using QR Code."""
    if not API_ID or not API_HASH:
        print("Error: API_ID or API_HASH not found in .env.")
        return None

    client = TelegramClient(StringSession(""), API_ID, API_HASH)
    await client.connect()
    
    if await client.is_user_authorized():
         print("Client is already authorized!")
         return client
         
    print("\nGenerating QR Login...")
    qr_login_obj = await client.qr_login()
    print("Scan the QR Code on the screen or open the following link in the Telegram app:")
    print(qr_login_obj.url)
    print("\n")
    
    # Generate and print the physical QR Code in the terminal
    qr = qrcode.QRCode(version=1, box_size=1, border=1)
    qr.add_data(qr_login_obj.url)
    qr.make(fit=True)
    
    # Invert the background/foreground to display correctly on dark terminals
    f = io.StringIO()
    qr.print_ascii(out=f, invert=True)
    f.seek(0)
    print(f.read())
    
    # Wait for the user to scan the QR code
    try:
        await qr_login_obj.wait(timeout=60)
        print("\nQR Login Successful!")
        
        # Determine user info to save session
        me = await client.get_me()
        phone = me.phone if me.phone else me.username
        if not phone:
             phone = str(me.id)
             
        session_file_name = os.path.join(SESSIONS_DIR, f"{phone}.session")
        new_session_string = client.session.save()
        with open(session_file_name, 'w') as f:
            f.write(new_session_string)
            
        print(f"Session saved as '{session_file_name}'.")
        return client
        
    except Exception as e:
        print(f"Failed to login via QR (possibly timeout): {e}")
        await client.disconnect()
        return None

async def login_existing_session(session_path):
    """Login using an existing session."""
    if not API_ID or not API_HASH:
        print("Error: API_ID or API_HASH not found in .env.")
        return None
        
    try:
        with open(session_path, 'r') as f:
            session_string = f.read().strip()
            
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        await client.connect()
        
        if not await client.is_user_authorized():
            print("Session is invalid or expired. Please login again.")
            await client.disconnect()
            return None
            
        print(f"Successfully connected using session: {os.path.basename(session_path)}")
        return client
    except Exception as e:
        print(f"Failed to read session: {e}")
        return None
