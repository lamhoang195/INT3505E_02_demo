"""
User Service - Shared business logic for all API versions
"""
import json
import os
from typing import List, Optional, Dict
import hashlib

class UserService:
    def __init__(self, data_file='backend/data/users.json'):
        self.data_file = data_file
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure data directory and file exist"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            # Create default admin user
            default_users = [{
                'id': '1',
                'username': 'admin',
                'password': self._hash_password('admin123'),
                'role': 'admin',
                'full_name': 'Administrator'
            }]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, ensure_ascii=False, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _read_users(self) -> List[Dict]:
        """Read all users from storage"""
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _write_users(self, users: List[Dict]):
        """Write users to storage"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (without passwords)"""
        users = self._read_users()
        return [{k: v for k, v in user.items() if k != 'password'} for user in users]
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get a user by ID (without password)"""
        users = self._read_users()
        for user in users:
            if user['id'] == user_id:
                return {k: v for k, v in user.items() if k != 'password'}
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get a user by username (with password for authentication)"""
        users = self._read_users()
        for user in users:
            if user['username'] == username:
                return user
        return None
    
    def create_user(self, user_data: Dict) -> Dict:
        """Create a new user"""
        users = self._read_users()
        
        # Check if username already exists
        if any(user['username'] == user_data['username'] for user in users):
            raise ValueError("Username already exists")
        
        # Generate new ID
        if users:
            max_id = max(int(user['id']) for user in users)
            new_id = str(max_id + 1)
        else:
            new_id = "1"
        
        new_user = {
            'id': new_id,
            'username': user_data['username'],
            'password': self._hash_password(user_data['password']),
            'role': user_data.get('role', 'user'),
            'full_name': user_data.get('full_name', '')
        }
        
        users.append(new_user)
        self._write_users(users)
        
        # Return without password
        return {k: v for k, v in new_user.items() if k != 'password'}
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user"""
        user = self.get_user_by_username(username)
        if user and user['password'] == self._hash_password(password):
            return {k: v for k, v in user.items() if k != 'password'}
        return None
    
    def update_user(self, user_id: str, user_data: Dict) -> Optional[Dict]:
        """Update a user"""
        users = self._read_users()
        for i, user in enumerate(users):
            if user['id'] == user_id:
                if 'password' in user_data:
                    user_data['password'] = self._hash_password(user_data['password'])
                
                users[i].update({k: v for k, v in user_data.items() if k != 'id'})
                self._write_users(users)
                return {k: v for k, v in users[i].items() if k != 'password'}
        return None
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        users = self._read_users()
        for i, user in enumerate(users):
            if user['id'] == user_id:
                users.pop(i)
                self._write_users(users)
                return True
        return False

