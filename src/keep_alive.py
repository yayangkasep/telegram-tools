import os
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from src.utils import print_header, get_integer_input
from src.auth import get_available_sessions, API_ID, API_HASH

async def keep_alive_single(session_path):
    """Runs a keep-alive loop for a single session."""
    if not API_ID or not API_HASH:
        print("Error: API_ID or API_HASH not found in .env.")
        return
        
    session_name = os.path.basename(session_path)
    print(f"\nStarting keep-alive for {session_name}...")
    
    try:
        with open(session_path, 'r') as f:
            session_string = f.read().strip()
            
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        await client.connect()
        
        if not await client.is_user_authorized():
            print(f"Session {session_name} is invalid/expired. Cannot keep alive.")
            await client.disconnect()
            return
            
        print(f"Successfully connected to {session_name}. Account is now ONLINE.")
        print("Press Ctrl+C to stop the keep-alive process and return.")
        
        # Keep the client running indefinitely
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        print(f"\nStopping keep-alive for {session_name}...")
    except Exception as e:
        print(f"\nError in keep-alive for {session_name}: {e}")
    finally:
        if 'client' in locals() and client.is_connected():
            await client.disconnect()

async def background_keep_alive(session_path):
    """Background task to keep a session alive without blocking the main loop."""
    try:
        with open(session_path, 'r') as f:
            session_string = f.read().strip()
            
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        await client.connect()
        
        if not await client.is_user_authorized():
            print(f"\n[Warning] Session {os.path.basename(session_path)} is invalid. Skipping.")
            await client.disconnect()
            return
            
        print(f"\n[Info] Session {os.path.basename(session_path)} is ONLINE.")
        await client.run_until_disconnected()
    except Exception as e:
         print(f"\n[Error] Keep-alive failed for {os.path.basename(session_path)}: {e}")

async def keep_alive_mass(sessions):
    """Runs keep-alive for ALL provided sessions sequentially, 10 seconds each."""
    print(f"\nStarting sequential keep-alive for {len(sessions)} sessions...")
    print("Each session will be online for 10 seconds. Press Ctrl+C to stop.\n")
    
    try:
        for session_path in sessions:
            session_name = os.path.basename(session_path)
            print(f"[Connecting] {session_name}...")
            
            try:
                with open(session_path, 'r') as f:
                    session_string = f.read().strip()
                    
                client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
                await client.connect()
                
                if not await client.is_user_authorized():
                    print(f"[Warning] Session {session_name} is invalid. Skipping.")
                    await client.disconnect()
                    continue
                    
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {session_name} is now ONLINE.")
                
                # Wait for 10 seconds while keeping the client connected
                await asyncio.sleep(10)
                
                # Disconnect and record last seen
                await client.disconnect()
                last_seen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[Disconnected] {session_name} - Last Seen: {last_seen}\n")
                
            except Exception as e:
                 print(f"[Error] Failed processing {session_name}: {e}\n")
                 if 'client' in locals() and client.is_connected():
                     await client.disconnect()
                     
        print("\n=== All accounts have been successfully processed. ===")
        
    except KeyboardInterrupt:
        print("\nStopping sequential keep-alive process...")

async def keep_alive_menu():
    """Menu for the Keep-Alive Auto-Online feature."""
    while True:
        print_header("Keep Sessions Alive (Auto-Online)")
        print("This feature will keep your sessions online to prevent account deletion.")
        print("WARNING: Leave this window open to keep the script running.\n")
        print("1. Auto Mass (Run ALL existing sessions)")
        print("2. Manual by Session (Choose ONE session)")
        print("3. Back to Main Menu")
        
        choice = get_integer_input("\nSelect an option: ", 1, 3)
        sessions = get_available_sessions()
        
        if choice == 1:
            if not sessions:
                print("\nNo session files found in the 'sessions/' directory.")
                input("\nPress Enter to go back...")
                continue
                
            await keep_alive_mass(sessions)
            input("\nPress Enter to go back...")
            
        elif choice == 2:
            if not sessions:
                print("\nNo session files found in the 'sessions/' directory.")
                input("\nPress Enter to go back...")
                continue
                
            print_header("Select Session to Keep Alive")
            for i, session_path in enumerate(sessions):
                filename = os.path.basename(session_path)
                print(f"[{i}] {filename}")
                
            print(f"[{len(sessions)}] Back")
            
            session_choice = get_integer_input("\nEnter session number: ", 0, len(sessions))
            if session_choice == len(sessions):
                continue
                
            selected_session = sessions[session_choice]
            await keep_alive_single(selected_session)
            input("\nPress Enter to go back...")
            
        elif choice == 3:
            return
