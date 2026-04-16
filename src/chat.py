from telethon.tl.types import User
from src.utils import clear_screen, get_integer_input, print_header

async def get_personal_chats(client):
    """Gets a list of personal/private chats (not groups or channels)."""
    personal_chats = []
    async for dialog in client.iter_dialogs():
        if dialog.is_user:
            personal_chats.append(dialog)
    return personal_chats

async def view_personal_chats(client):
    """Displays the list of personal chats."""
    print_header("List of Personal Chats")
    print("Finding your personal chats...\n")
    
    chats = await get_personal_chats(client)
    
    if not chats:
        print("No personal chats found.")
        input("\nPress Enter to go back...")
        return
        
    # Display the last 20 chats
    display_limit = min(20, len(chats))
    print(f"Displaying {display_limit} out of {len(chats)} total personal chats:\n")
    
    for i in range(display_limit):
        chat = chats[i]
        last_message = chat.message.text if chat.message and hasattr(chat.message, 'text') else "<Media/System Message>"
        last_message = last_message[:50] + '...' if last_message and len(last_message) > 50 else last_message
        print(f"[{i}] {chat.name} -> {last_message}")

    input("\nPress Enter to go back...")

async def open_chat_history(client):
    """Reads the message history from a personal chat."""
    print_header("Read Chat History")
    chats = await get_personal_chats(client)
    
    if not chats:
         print("No personal chats found.")
         input("\nPress Enter to go back...")
         return
         
    limit = min(20, len(chats))
    for i in range(limit):
         print(f"[{i}] {chats[i].name}")
         
    choice = get_integer_input("\nSelect the chat number to read: ", 0, limit - 1)
    selected_chat = chats[choice]
    
    print_header(f"Chat History - {selected_chat.name}")
    print("Fetching the last 15 messages...\n")
    
    try:
        messages = await client.get_messages(selected_chat.entity, limit=15)
        # Display messages from oldest to newest
        for msg in reversed(messages):
            sender = "You" if msg.out else selected_chat.name
            text = msg.text if msg.text else "<Media File>"
            print(f"{sender}: {text}")
    except Exception as e:
        print(f"Failed to fetch messages: {e}")

    input("\nPress Enter to go back...")

async def send_message_to_chat(client):
    """Sends a message to one of the personal chats."""
    print_header("Send Personal Message")
    chats = await get_personal_chats(client)
    
    if not chats:
         print("No personal chats found.")
         input("\nPress Enter to go back...")
         return
         
    limit = min(20, len(chats))
    for i in range(limit):
         print(f"[{i}] {chats[i].name}")
         
    choice = get_integer_input("\nSelect the contact number: ", 0, limit - 1)
    selected_chat = chats[choice]
    
    print(f"\nSend message to: {selected_chat.name}")
    print("Type your message (leave blank and press Enter to cancel):")
    
    message_text = input("> ").strip()
    if not message_text:
        print("\nMessage is empty. Cancelled.")
        input("\nPress Enter to go back...")
        return
        
    print("\nSending message...")
    try:
        await client.send_message(selected_chat.entity, message_text)
        print("Message sent successfully!")
    except Exception as e:
        print(f"Failed to send message: {e}")
        
    input("\nPress Enter to go back...")
