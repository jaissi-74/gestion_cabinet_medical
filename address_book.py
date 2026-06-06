import os
import csv
import sqlite3
from contact import Contact


FILE_PATH = "contacts.txt"
DB_PATH = "contacts.db"


# ─────────────────────────────────────────────
#  PART 1 — In-memory address book (list)
# ─────────────────────────────────────────────

class AddressBook:
    """
    Part 1: Stores contacts in a Python list (in-memory only).
    Data is lost when the program closes.
    """

    def __init__(self):
        self.contacts = []

    def add_contact(self, name, email, phone):
        if not Contact.validate_email(email):
            return False, "Invalid email format."
        if not Contact.validate_phone(phone):
            return False, "Invalid phone format."
        if self._find_by_email(email):
            return False, "A contact with this email already exists."
        self.contacts.append(Contact(name, email, phone))
        return True, "Contact added successfully."

    def remove_contact(self, email):
        contact = self._find_by_email(email)
        if contact:
            self.contacts.remove(contact)
            return True, "Contact removed."
        return False, "Contact not found."

    def display_contacts(self):
        if not self.contacts:
            return []
        return sorted(self.contacts, key=lambda c: c.name.lower())

    def _find_by_email(self, email):
        for c in self.contacts:
            if c.email.lower() == email.lower():
                return c
        return None


# ─────────────────────────────────────────────
#  PART 2 — File-based address book (txt)
# ─────────────────────────────────────────────

class AddressBookFile:
    """
    Part 2: Stores contacts persistently in a text file.
    Each line: name,email,phone

    Difference from list:
    - List: fast, simple, but data disappears when program closes.
    - File: data persists between sessions, but slower (reads/writes disk each time).
    """

    def __init__(self, filepath=FILE_PATH):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            open(self.filepath, 'w').close()

    def _load(self):
        contacts = []
        with open(self.filepath, 'r', encoding='utf-8') as f:
            for line in f:
                c = Contact.from_string(line)
                if c:
                    contacts.append(c)
        return contacts

    def _save(self, contacts):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            for c in contacts:
                f.write(c.to_string() + '\n')

    def add_contact(self, name, email, phone):
        if not Contact.validate_email(email):
            return False, "Invalid email format."
        if not Contact.validate_phone(phone):
            return False, "Invalid phone format."
        contacts = self._load()
        for c in contacts:
            if c.email.lower() == email.lower():
                return False, "A contact with this email already exists."
        contacts.append(Contact(name, email, phone))
        self._save(contacts)
        return True, "Contact added and saved to file."

    def remove_contact(self, email):
        contacts = self._load()
        new_contacts = [c for c in contacts if c.email.lower() != email.lower()]
        if len(new_contacts) == len(contacts):
            return False, "Contact not found."
        self._save(new_contacts)
        return True, "Contact removed and file updated."

    def display_contacts(self):
        contacts = self._load()
        return sorted(contacts, key=lambda c: c.name.lower())

    def export_to_csv(self, csv_path="contacts_export.csv"):
        contacts = self._load()
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Email", "Phone"])
            for c in contacts:
                writer.writerow([c.name, c.email, c.phone])
        return True, f"Exported to {csv_path}"


# ─────────────────────────────────────────────
#  PART 5 — SQLite-based address book
# ─────────────────────────────────────────────

class AddressBookDB:
    """
    Part 5: Stores contacts in an SQLite database.
    Admin accounts are also stored in the database.
    """

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    category TEXT DEFAULT 'General',
                    address TEXT DEFAULT '',
                    company TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def add_contact(self, name, email, phone, category='General', address='', company=''):
        if not Contact.validate_email(email):
            return False, "Invalid email format."
        if not Contact.validate_phone(phone):
            return False, "Invalid phone format."
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO contacts (name, email, phone, category, address, company) VALUES (?,?,?,?,?,?)",
                    (name, email, phone, category, address, company)
                )
                conn.commit()
            return True, "Contact added to database."
        except sqlite3.IntegrityError:
            return False, "A contact with this email already exists."

    def remove_contact(self, email):
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM contacts WHERE email=?", (email.lower(),))
            conn.commit()
            if cursor.rowcount == 0:
                return False, "Contact not found."
        return True, "Contact deleted from database."

    def display_contacts(self):
        with self._connect() as conn:
            # 1. On sélectionne TOUTES les colonnes de la table SQL
            rows = conn.execute("SELECT name, email, phone, category, address, company FROM contacts ORDER BY name").fetchall()
        
        contacts_complets = []
        for r in rows:
            # 2. On crée le contact de base
            c = Contact(r[0], r[1], r[2])
            # 3. On lui ré-attache ses informations supplémentaires de la BDD
            c.category = r[3]
            c.address = r[4]
            c.company = r[5]
            contacts_complets.append(c)
            
        return contacts_complets

    def search(self, query):
        with self._connect() as conn:
            # Même chose ici pour la recherche : on prend tout !
            rows = conn.execute(
                "SELECT name, email, phone, category, address, company FROM contacts WHERE name LIKE ? OR email LIKE ?",
                (f"%{query}%", f"%{query}%")
            ).fetchall()
            
        contacts_complets = []
        for r in rows:
            c = Contact(r[0], r[1], r[2])
            c.category = r[3]
            c.address = r[4]
            c.company = r[5]
            contacts_complets.append(c)
            
        return contacts_complets
    
    def update_contact(self, name, email, phone, category='General', address='', company=''):
        """Met à jour les informations d'un contact existant via son email (clé unique)"""
        try:
            with self._connect() as conn:
                conn.execute("""
                    UPDATE contacts 
                    SET name = ?, phone = ?, category = ?, address = ?, company = ?
                    WHERE email = ?
                """, (name, phone, category, address, company, email.lower()))
                conn.commit()
            return True, "Contact mis à jour avec succès."
        except sqlite3.Error as e:
            return False, f"Erreur lors de la modification : {e}"

    def export_csv(self, path="db_export.csv"):
        contacts = self.display_contacts()
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Email", "Phone"])
            for c in contacts:
                writer.writerow([c.name, c.email, c.phone])
        return True, f"Exported {len(contacts)} contacts to {path}"
