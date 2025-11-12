"""
Donation Service - Quản lý quyên góp cho thư viện
"""
import json
import os
from typing import List, Optional, Dict
from datetime import datetime

class DonationService:
    def __init__(self, data_file='backend/data/donations.json'):
        self.data_file = data_file
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure data directory and file exist"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def _read_donations(self) -> List[Dict]:
        """Read all donation records from storage"""
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _write_donations(self, donations: List[Dict]):
        """Write donation records to storage"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(donations, f, ensure_ascii=False, indent=2)
    
    def create_donation(self, donation_data: Dict) -> Dict:
        """Create a new donation record"""
        donations = self._read_donations()
        
        # Generate new ID
        if donations:
            max_id = max(int(d['id']) for d in donations)
            new_id = str(max_id + 1)
        else:
            new_id = "1"
        
        new_donation = {
            'id': new_id,
            'user_id': donation_data.get('user_id'),
            'borrow_id': donation_data.get('borrow_id'),
            'amount': donation_data.get('amount', 0),
            'donation_date': datetime.now().isoformat(),
            'message': donation_data.get('message', '')
        }
        
        donations.append(new_donation)
        self._write_donations(donations)
        return new_donation
    
    def get_all_donations(self) -> List[Dict]:
        """Get all donation records"""
        return self._read_donations()
    
    def get_donations_by_user(self, user_id: str) -> List[Dict]:
        """Get all donations by a user"""
        donations = self._read_donations()
        return [d for d in donations if d['user_id'] == user_id]
    
    def get_total_donations(self) -> float:
        """Get total amount of all donations"""
        donations = self._read_donations()
        return sum(float(d.get('amount', 0)) for d in donations)

