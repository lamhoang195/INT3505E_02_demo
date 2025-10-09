"""
Borrow Service - Shared business logic for all API versions
"""
import json
import os
from typing import List, Optional, Dict
from datetime import datetime, timedelta

class BorrowService:
    def __init__(self, data_file='backend/data/borrows.json'):
        self.data_file = data_file
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure data directory and file exist"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def _read_borrows(self) -> List[Dict]:
        """Read all borrow records from storage"""
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _write_borrows(self, borrows: List[Dict]):
        """Write borrow records to storage"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(borrows, f, ensure_ascii=False, indent=2)
    
    def get_all_borrows(self) -> List[Dict]:
        """Get all borrow records"""
        return self._read_borrows()
    
    def get_borrow_by_id(self, borrow_id: str) -> Optional[Dict]:
        """Get a borrow record by ID"""
        borrows = self._read_borrows()
        for borrow in borrows:
            if borrow['id'] == borrow_id:
                return borrow
        return None
    
    def get_borrows_by_user(self, user_id: str) -> List[Dict]:
        """Get all borrow records for a user"""
        borrows = self._read_borrows()
        return [b for b in borrows if b['user_id'] == user_id]
    
    def get_active_borrows(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get active (not returned) borrow records"""
        borrows = self._read_borrows()
        active = [b for b in borrows if b['status'] == 'borrowed']
        if user_id:
            active = [b for b in active if b['user_id'] == user_id]
        return active
    
    def create_borrow(self, borrow_data: Dict) -> Dict:
        """Create a new borrow record"""
        borrows = self._read_borrows()
        
        # Generate new ID
        if borrows:
            max_id = max(int(borrow['id']) for borrow in borrows)
            new_id = str(max_id + 1)
        else:
            new_id = "1"
        
        # Calculate due date (14 days from now)
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=14)
        
        new_borrow = {
            'id': new_id,
            'user_id': borrow_data['user_id'],
            'book_id': borrow_data['book_id'],
            'borrow_date': borrow_date.isoformat(),
            'due_date': due_date.isoformat(),
            'return_date': None,
            'status': 'borrowed'
        }
        
        borrows.append(new_borrow)
        self._write_borrows(borrows)
        return new_borrow
    
    def return_book(self, borrow_id: str) -> Optional[Dict]:
        """Mark a borrow record as returned"""
        borrows = self._read_borrows()
        for i, borrow in enumerate(borrows):
            if borrow['id'] == borrow_id and borrow['status'] == 'borrowed':
                borrows[i]['return_date'] = datetime.now().isoformat()
                borrows[i]['status'] = 'returned'
                self._write_borrows(borrows)
                return borrows[i]
        return None
    
    def get_borrow_history(self, user_id: Optional[str] = None, book_id: Optional[str] = None) -> List[Dict]:
        """Get borrow history with optional filters"""
        borrows = self._read_borrows()
        
        if user_id:
            borrows = [b for b in borrows if b['user_id'] == user_id]
        
        if book_id:
            borrows = [b for b in borrows if b['book_id'] == book_id]
        
        return borrows

