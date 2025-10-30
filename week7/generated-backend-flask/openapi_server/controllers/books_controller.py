import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.controllers_books_controller_get_books200_response import ControllersBooksControllerGetBooks200Response  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server import util


def controllers_books_controller_get_books(title=None, author=None, available=None):  # noqa: E501
    """Get all books

    Retrieve a list of all books in the system # noqa: E501

    :param title: Filter books by title (partial match)
    :type title: str
    :param author: Filter books by author (partial match)
    :type author: str
    :param available: Filter by availability status
    :type available: bool

    :rtype: Union[ControllersBooksControllerGetBooks200Response, Tuple[ControllersBooksControllerGetBooks200Response, int], Tuple[ControllersBooksControllerGetBooks200Response, int, Dict[str, str]]
    """
    # Sample books data
    books = [
        {
            "id": 1,
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "publisher": "Prentice Hall",
            "quantity": 5
        },
        {
            "id": 2,
            "title": "The Pragmatic Programmer",
            "author": "Andrew Hunt",
            "publisher": "Addison-Wesley",
            "quantity": 3
        },
        {
            "id": 3,
            "title": "Design Patterns",
            "author": "Gang of Four",
            "publisher": "Addison-Wesley",
            "quantity": 4
        }
    ]
    
    # Filter by title if provided
    if title:
        books = [b for b in books if title.lower() in b['title'].lower()]
    
    # Filter by author if provided
    if author:
        books = [b for b in books if author.lower() in b['author'].lower()]
    
    # Return response
    response = {
        "success": True,
        "data": books,
        "count": len(books)
    }
    
    return response, 200
