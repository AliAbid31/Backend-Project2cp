"""
Remove test/hardcoded messages from database - comprehensive cleanup
"""
import sqlite3

def clean_test_messages():
    try:
        conn = sqlite3.connect('tutoratup.db')
        cursor = conn.cursor()
        
        # Get all messages first
        cursor.execute("SELECT id, content FROM messages ORDER BY timestamp DESC")
        all_messages = cursor.fetchall()
        
        print("Analyzing messages for cleanup...")
        print(f"Total messages: {len(all_messages)}\n")
        
        # List of specific test messages to remove
        test_patterns = [
            'eaeaeaaee',
            'eaeaeaeaeaeae',
            'eaaeaeaeaeeaae',
            'شيشيشيشيششيشيشي',
            'يشيشيشيشيششيشيشي',
            'dadd',
            'dadadad',
            'je suis',
            'HHiii',
            'hdhiehd',
            'eiofjzioefj',
            'jojzfzenidfjz',
            'Hello! This is test message',
            'Hi! Thanks for message',
            'jhkhjhk',
            'odfjlzjef',
            'kkkkkk',
            'Hii',
            'JI',
        ]
        
        print("Messages to remove:")
        messages_to_delete = []
        
        # Very short obvious test messages
        for msg_id, content in all_messages:
            is_test = False
            
            # Check against patterns
            for pattern in test_patterns:
                if pattern.lower() in content.lower():
                    is_test = True
                    break
            
            # Check for very short messages that are likely test
            if not is_test and len(content.strip()) <= 3:
                if content.strip() not in ['Hi', 'Ok', 'Yes', 'No']:  # Allow some short real messages
                    is_test = True
            
            # Check for obvious nonsense patterns
            if not is_test:
                # Multiple repeated characters (more than 4 same char)
                for char in content:
                    if content.count(char) > 5:
                        is_test = True
                        break
            
            if is_test:
                messages_to_delete.append((msg_id, content))
                print(f"  ❌ ID {msg_id}: {content[:60]}")
        
        print(f"\nRemoving {len(messages_to_delete)} test messages...\n")
        
        for msg_id, content in messages_to_delete:
            cursor.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
        
        conn.commit()
        
        # Verify cleanup
        cursor.execute("SELECT COUNT(*) FROM messages")
        total = cursor.fetchone()[0]
        print(f"✅ Clean up complete! Total messages remaining: {total}")
        
        # Show remaining messages
        cursor.execute("SELECT id, sender_id, receiver_id, content, timestamp FROM messages ORDER BY timestamp DESC")
        print("\n📨 Messages remaining in database:")
        print("-" * 100)
        remaining_messages = cursor.fetchall()
        for row in remaining_messages:
            msg_id, sender, receiver, content, timestamp = row
            content_preview = content[:65] if len(content) > 65 else content
            print(f"ID: {msg_id:2d} | From: {sender} → {receiver} | {content_preview:65s} | {timestamp}")
        
        print(f"\n✨ Database cleaned! Kept {total} real messages")
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.close()

if __name__ == "__main__":
    clean_test_messages()
