import unittest

from flask import json

from openapi_server.models.controllers_books_controller_get_books200_response import ControllersBooksControllerGetBooks200Response  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.test import BaseTestCase


class TestBooksController(BaseTestCase):
    """BooksController integration test stubs"""

    def test_controllers_books_controller_get_books(self):
        """Test case for controllers_books_controller_get_books

        Get all books
        """
        query_string = [('title', 'title_example'),
                        ('author', 'author_example'),
                        ('available', True)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/v1/books',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
