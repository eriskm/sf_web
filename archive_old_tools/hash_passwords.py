import sqlite3
from werkzeug.security import generate_password_hash

def main():
    print("Migrating plaintext passwords to secure hashes...")
    try:
        conn = sqlite3.connect('sukabumi_flasher.db')
        cursor = conn.cursor()
        
        # Ambil semua user
        cursor.execute("SELECT id, username, password FROM users")
        users = cursor.fetchall()
        
        updated_count = 0
        for user_id, username, password in users:
            # Lewati jika password sudah di-hash (werkzeug hash biasanya diawali dengan 'scrypt:' atau 'pbkdf2:sha256:')
            if password and (password.startswith('scrypt:') or password.startswith('pbkdf2:')):
                print(f"Skipping user {username}, password already hashed.")
                continue
                
            if not password:
                print(f"Warning: User {username} has no password!")
                continue
                
            # Generate hash
            hashed_pw = generate_password_hash(password)
            
            # Update database
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_pw, user_id))
            updated_count += 1
            print(f"Updated password for user: {username}")
            
        conn.commit()
        conn.close()
        print(f"Migration completed successfully. Updated {updated_count} accounts.")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == '__main__':
    main()
