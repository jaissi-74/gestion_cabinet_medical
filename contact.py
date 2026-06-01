import re


class Contact:
    """Represents a single contact with name, email, and phone number."""

    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone

    @staticmethod
    def validate_email(email):
        """Returns True if the email format is valid."""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone):
        """Returns True if the phone contains only digits, spaces, +, or -."""
        pattern = r'^[\d\s\+\-]{6,15}$'
        return re.match(pattern, phone) is not None

    def to_string(self):
        """Returns a formatted string representation of the contact."""
        return f"{self.name},{self.email},{self.phone}"

    @classmethod
    def from_string(cls, line):
        """Creates a Contact from a comma-separated string (used for file reading)."""
        parts = line.strip().split(',')
        if len(parts) == 3:
            return cls(parts[0], parts[1], parts[2])
        return None

    def __str__(self):
        return f"Name: {self.name} | Email: {self.email} | Phone: {self.phone}"

    def __repr__(self):
        return f"Contact(name='{self.name}', email='{self.email}', phone='{self.phone}')"
