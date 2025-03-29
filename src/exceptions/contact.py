"""Custom exceptions for contact-related operations.

This module defines custom exceptions that can be raised during contact operations.
"""


class ContactException(Exception):
    """Base exception for all contact-related errors."""
    pass


class ContactAlreadyExists(ContactException):
    """Exception raised when attempting to create a contact with an email that already exists."""
    pass
