import os
from telethon import TelegramClient
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import DeleteChatUserRequest
from src.utils import clear_screen, get_integer_input, print_header

async def get_all_groups_and_channels(client):
    """Get a list of all groups and channels."""
    chats = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            chats.append(dialog)
    return chats

async def auto_leave_menu(client):
    """Menu for Auto Leave Group / Channel feature."""
    while True:
        print_header("Auto Leave Group & Channel")
        print("1. Leave Mass (All Groups & Channels)")
        print("2. Choose Specific (Select from a list)")
        print("3. Back to App Menu")
        
        choice = get_integer_input("\nSelect an option: ", 1, 3)
        
        if choice == 1:
            await leave_mass(client)
        elif choice == 2:
            await leave_specific(client)
        elif choice == 3:
            return

async def process_leave(client, chat):
    """Helper function to perform leave action on a single chat."""
    try:
        # Telethon differentiates leaving methods for Megagroups/Channels vs Basic Chats
        if chat.is_channel:
             # For Channels and Megagroups
             await client(LeaveChannelRequest(chat.entity))
        else:
             # For Basic Groups
             await client(DeleteChatUserRequest(chat.id, 'me'))
             
        print(f"[Success] Left: {chat.name}")
    except Exception as e:
        print(f"[Failed] Leaving {chat.name}: {e}")

async def leave_mass(client):
    """Leave all groups and channels."""
    print_header("Mass Leave (Warning)")
    print("Fetching your groups and channels...\n")
    
    chats = await get_all_groups_and_channels(client)
    
    if not chats:
        print("You are not in any groups or channels.")
        input("\nPress Enter to go back...")
        return
        
    print(f"Found {len(chats)} groups/channels.")
    print("WARNING: This action will make you leave ALL groups and channels.")
    
    confirm = input("Are you sure? (Type 'CONFIRM' to proceed): ")
    if confirm != 'CONFIRM':
        print("\nCancelled.")
        input("\nPress Enter to go back...")
        return
        
    print("\nStarting mass leave process...\n")
    for chat in chats:
        await process_leave(client, chat)
        
    print("\n[Done] Mass leave process completed.")
    input("\nPress Enter to go back...")

async def leave_specific(client):
    """Leave a specific group/channel chosen by the user."""
    print_header("Specific Leave")
    print("Fetching your groups and channels...\n")
    
    chats = await get_all_groups_and_channels(client)
    
    if not chats:
        print("You are not in any groups or channels.")
        input("\nPress Enter to go back...")
        return
        
    for i, chat in enumerate(chats):
        chat_type = "Channel" if chat.is_channel and not chat.is_group else "Group"
        print(f"[{i}] {chat.name} ({chat_type})")
        
    print(f"[{len(chats)}] Cancel / Back")
    
    choice = get_integer_input("\nSelect the group/channel number you want to leave: ", 0, len(chats))
    
    if choice == len(chats):
        return
        
    selected_chat = chats[choice]
    print(f"\nYou are about to leave: {selected_chat.name}")
    confirm = input("Are you sure? (y/n): ").lower()
    
    if confirm == 'y':
        await process_leave(client, selected_chat)
    else:
        print("Cancelled.")
        
    input("\nPress Enter to go back...")
