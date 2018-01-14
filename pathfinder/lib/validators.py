"""Validators lib application file."""
from formencode.schema import Schema
from formencode.validators import OneOf, String, URL


class UriData(Schema):
    """Validate URI data received from CSV or user input.

    All fields are required, cannot be None and no extra fields are allowed.
    """

    title = String(not_empty=True)
    URI = URL(not_empty=True)
    notify = OneOf(
        ["always", "valid", "invalid"],
        not_empty=True
    )
