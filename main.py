import os
import sys
import asyncio

from src.utils import clear_screen, print_header, get_integer_input
from src.auth import get_available_sessions, login_with_phone, login_with_qr, login_existing_session
from src.scraper import scrape_members
from src.chat import view_personal_chats, open_chat_history, send_message_to_chat
from src.keep_alive import keep_alive_menu
from src.leave import auto_leave_menu

async def main_menu():
    client = None
    
    while True:
        print_header("Telegram Tools - Main Menu")
        print("1. Login (New)")
        print("2. Login with Existing Session")
        print("3. Keep Sessions Alive (Auto-Online)")
        print("4. Exit")
        
        choice = get_integer_input("\nSelect an option: ", 1, 4)
        
        if choice == 1:
            clear_screen()
            print_header("Select Login Method")
            print("1. Phone Number (OTP)")
            print("2. QR Code")
            print("3. Back")
            
            login_choice = get_integer_input("\nSelect method: ", 1, 3)
            if login_choice == 1:
                client = await login_with_phone()
            elif login_choice == 2:
                client = await login_with_qr()
                
            if client:
                break # Proceed to app menu
                
        elif choice == 2:
            sessions = get_available_sessions()
            if not sessions:
                print("\nNo session files found in the 'sessions/' directory.")
                input("\nPress Enter to go back...")
                continue
                
            clear_screen()
            print_header("Select Session")
            for i, session_path in enumerate(sessions):
                filename = os.path.basename(session_path)
                print(f"[{i}] {filename}")
                
            print(f"[{len(sessions)}] Back")
            
            session_choice = get_integer_input("\nEnter session number: ", 0, len(sessions))
            
            if session_choice == len(sessions):
                continue
                
            selected_session = sessions[session_choice]
            client = await login_existing_session(selected_session)
            if client:
                break # Proceed to app menu
                
        elif choice == 3:
            await keep_alive_menu()
            
        elif choice == 4:
            print("\nExiting program. Goodbye!")
            return

    # App Menu (After Login)
    if client:
        await app_menu(client)

async def app_menu(client):
    while True:
        print_header("Telegram Tools - App Menu")
        print("1. Scrape Members (Group/Channel)")
        print("2. View Personal Chats")
        print("3. Read Chat History")
        print("4. Send Message to Chat")
        print("5. Auto Leave (Group/Channel)")
        print("6. Exit")
        
        choice = get_integer_input("\nSelect an option: ", 1, 6)
        
        if choice == 1:
             await scrape_members(client)
        elif choice == 2:
             await view_personal_chats(client)
        elif choice == 3:
             await open_chat_history(client)
        elif choice == 4:
             await send_message_to_chat(client)
        elif choice == 5:
             await auto_leave_menu(client)
        elif choice == 6:
             print("\nGoodbye!")
             await client.disconnect()
             return

if __name__ == "__main__":
    while True:
        asyncio.run(main_menu())
        break
