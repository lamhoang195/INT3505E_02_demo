"""
Book Service - Shared business logic for all API versions
"""
import json
import os
from typing import List, Optional, Dict

class BookService:
    def __init__(self, data_file='backend/data/books.json'):
        self.data_file = data_file
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure data directory and file exist"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def _read_books(self) -> List[Dict]:
        """Read all books from storage"""
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _write_books(self, books: List[Dict]):
        """Write books to storage"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
    
    def get_all_books(self) -> List[Dict]:
        """Get all books"""
        return self._read_books()
    
    def get_book_by_id(self, book_id: str) -> Optional[Dict]:
        """Get a book by ID"""
        books = self._read_books()
        for book in books:
            if book['id'] == book_id:
                return book
        return None
    
    def create_book(self, book_data: Dict) -> Dict:
        """Create a new book"""
        books = self._read_books()
        
        # Generate new ID
        if books:
            max_id = max(int(book['id']) for book in books)
            new_id = str(max_id + 1)
        else:
            new_id = "1"
        
        new_book = {
            'id': new_id,
            'title': book_data['title'],
            'author': book_data['author'],
            'isbn': book_data.get('isbn', ''),
            'quantity': book_data.get('quantity', 1),
            'available': book_data.get('quantity', 1)
        }
        
        books.append(new_book)
        self._write_books(books)
        return new_book
    
    def update_book(self, book_id: str, book_data: Dict) -> Optional[Dict]:
        """Update a book"""
        books = self._read_books()
        for i, book in enumerate(books):
            if book['id'] == book_id:
                books[i].update({
                    'title': book_data.get('title', book['title']),
                    'author': book_data.get('author', book['author']),
                    'isbn': book_data.get('isbn', book.get('isbn', '')),
                    'quantity': book_data.get('quantity', book.get('quantity', 1)),
                    'available': book_data.get('available', book.get('available', 1))
                })
                self._write_books(books)
                return books[i]
        return None
    
    def delete_book(self, book_id: str) -> bool:
        """Delete a book"""
        books = self._read_books()
        for i, book in enumerate(books):
            if book['id'] == book_id:
                books.pop(i)
                self._write_books(books)
                return True
        return False
    
    def update_availability(self, book_id: str, change: int) -> bool:
        """Update book availability (for borrowing/returning)"""
        books = self._read_books()
        for i, book in enumerate(books):
            if book['id'] == book_id:
                new_available = book.get('available', 0) + change
                if 0 <= new_available <= book.get('quantity', 0):
                    books[i]['available'] = new_available
                    self._write_books(books)
                    return True
                return False
        return False

