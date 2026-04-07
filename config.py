"""
config.py
Central configuration file for the Flask application.
Change DB settings here if needed.
"""

import os

class Config:
    # Secret key for session management (change this in production!)
    SECRET_KEY = os.environ.get("SECRET_KEY", "college_leave_secret_key_2024")

    # MySQL database configuration
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = ""       # XAMPP default is empty; change if yours is different
    MYSQL_DB = "college_leave_system"
    MYSQL_CURSORCLASS = "DictCursor"   # Returns rows as dictionaries
