import os
import csv
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantCreator, ChannelParticipantAdmin
from telethon.errors.rpcerrorlist import UserNotParticipantError
from src.utils import clear_screen, get_integer_input, print_header

EXPORTS_DIR = "exports"

if not os.path.exists(EXPORTS_DIR):
    os.makedirs(EXPORTS_DIR)

async def scrape_members(client):
    """Scrape members from Groups/Channels to CSV."""
    print_header("Scrape Group/Channel Members")
    print("Fetching your groups and channels...\n")
    
    chats = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            chats.append(dialog)

    if not chats:
        print("No groups or channels found.")
        input("\nPress Enter to go back...")
        return

    for i, chat in enumerate(chats):
        chat_type = "Channel" if chat.is_channel and not chat.is_group else "Group"
        print(f"[{i}] {chat.name} ({chat_type})")

    choice = get_integer_input("\nEnter the number of the group/channel to scrape: ", 0, len(chats)-1)
    selected_chat = chats[choice]
    
    print(f"\nSelected: {selected_chat.name}")

    # Check ownership/role
    try:
        participant = await client(GetParticipantRequest(
            channel=selected_chat.entity,
            participant='me'
        ))
        if isinstance(participant.participant, (ChannelParticipantCreator, ChannelParticipantAdmin)):
            print("Your status: Admin/Creator here.")
        else:
            print("Your status: Regular member.")
    except UserNotParticipantError:
        print("You are no longer a participant here.")
        input("\nPress Enter to go back...")
        return
    except Exception as e:
        if hasattr(selected_chat.entity, 'creator') and selected_chat.entity.creator:
             print("Your status: Chat creator.")
        else:
             print("Your status: Member / Unverified role.")

    print("\nStarting to scrape members...")
    scraped_users = []
    
    try:
        async for user in client.iter_participants(selected_chat.entity):
            user_data = {
                'id': user.id,
                'first_name': user.first_name if user.first_name else '',
                'last_name': user.last_name if user.last_name else '',
                'username': user.username if user.username else '',
                'phone': user.phone if user.phone else ''
            }
            scraped_users.append(user_data)
            
            if len(scraped_users) % 100 == 0:
                print(f"Successfully scraped {len(scraped_users)} members...")
                
    except Exception as e:
        print(f"Warning during scraping (some channels hide members): {e}")

    print(f"\nProcess finished. Total members scraped: {len(scraped_users)}")

    if scraped_users:
        filename = f"{selected_chat.name.replace(' ', '_')}_members.csv"
        filename = "".join(c for c in filename if c.isalnum() or c in ('_', '.', '-'))
        export_path = os.path.join(EXPORTS_DIR, filename)
        
        print(f"Saving to {export_path}...")
        with open(export_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'first_name', 'last_name', 'username', 'phone'])
            writer.writeheader()
            writer.writerows(scraped_users)
            
        print(f"Successfully saved CSV file to {os.path.abspath(export_path)}")
    else:
        print("No members to save.")
        
    input("\nPress Enter to go back...")
