from database.db_handler import DatabaseHandler
from utils.hashing import check_password

class UserModel:
    def __init__(self):
        self.db = DatabaseHandler()

    def authenticate(self, username: str, password: str):
        if not username or not password:
            return None

        query = "SELECT id, username, password_hash, role FROM users WHERE username = ?"
        rows = self.db.execute_query(query, (username.strip(),), fetch=True)
        
        if not rows:
            return None

        u_id, username_val, p_hash, role_val = rows[0]
        if check_password(password, p_hash):
            return {
                'id': u_id,
                'username': username_val,
                'role': role_val
            }

        return None

    def get_by_username(self, username):
        query = "SELECT id, username, role FROM users WHERE username = ?"
        results = self.db.execute_query(query, (username,), fetch=True)
        return results[0] if results else None
