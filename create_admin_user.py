#!/usr/bin/env python
"""
Create an admin user in db.sqlite using a hashed password.
"""

from flat import _patch_collections_for_py3

_patch_collections_for_py3()
import getpass
import json
import os
from werkzeug.security import generate_password_hash

from storage.sql import StorageSqliteDB, User

PROJECT_PATH = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(PROJECT_PATH, "flat.json")


def load_db_path():
    default_db = os.path.join(PROJECT_PATH, "db.sqlite")
    if not os.path.isfile(CONFIG_PATH):
        return default_db
    try:
        with open(CONFIG_PATH) as f:
            data = json.load(f)
        db_name = data.get("db", "db.sqlite")
        return os.path.join(PROJECT_PATH, db_name)
    except Exception:
        return default_db


def main():
    db_path = load_db_path()
    print(f"Using database: {db_path}")
    db = StorageSqliteDB(db_path)
    username = input("Username: ").strip()
    if not username:
        print("Username required")
        return
    password = getpass.getpass("Password: ")
    if not password:
        print("Password required")
        return
    hashed = generate_password_hash(password)
    user = db.db.query(User).get(username)
    if user:
        user.password = hashed
        user.name = username
        print("Updating existing user.")
    else:
        user = User(id=username, name=username, password=hashed)
        db.db.add(user)
        print("Creating new user.")
    db.db.commit()
    db.db.close()
    print("Done.")


if __name__ == "__main__":
    main()
