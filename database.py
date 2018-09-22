"""
A class for database shit.
"""

import sqlite3

class Database:
    def __init__(self, db_file):
        self.db = sqlite3.connect(db_file, timeout=15.0)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.cursor = self.db.cursor()
        self.database_verify()

    def database_verify(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS `settings` ( `discord_auth_token` TEXT, `osu_api_key` TEXT )")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS `users` ( `discord_id` INTEGER UNIQUE, `osu_id` INTEGER, `days` INTEGER, `total` INTEGER, `last_checked` INTEGER, PRIMARY KEY(`discord_id`) )")

    def get_discord_auth(self):
        self.cursor.execute("SELECT `discord_auth_token` FROM `settings`")

        return self.cursor.fetchone()[0]

    def get_osu_api_key(self):
        self.cursor.execute("SELECT `osu_api_key` FROM `settings`")

        return self.cursor.fetchone()[0]
