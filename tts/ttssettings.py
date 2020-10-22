import sqlite3


class TTSSettings:
    """Stores user tts settings in a database"""
    def __init__(self):
        self.conn = sqlite3.connect('tts-settings.db')
        self._create_settings_table()

    def _create_settings_table(self):
        c = self.conn.cursor()

        c.execute("""\
        CREATE TABLE IF NOT EXISTS settings (
            id TEXT PRIMARY KEY,
            rate INTEGER NOT NULL,
            voice_id INTEGER NOT NULL,
            volume REAL NOT NULL
        );""")

    def create_user(self, user_id, rate=200, voice_id=0, volume=1.0):
        c = self.conn.cursor()

        c.execute("""\
        INSERT INTO settings(id, rate, voice_id, volume)
        VALUES(?,?,?,?)""", (user_id, rate, voice_id, volume))

        self.conn.commit()

    def update_user(self, user_id, rate=None, voice_id=None, volume=None):
        if not self.user_exists(user_id):
            self.create_user(user_id)

        c = self.conn.cursor()

        if rate is not None:
            c.execute("""\
            UPDATE settings
            SET rate = ?
            WHERE id = ?""", (rate, user_id))

        if voice_id is not None:
            c.execute("""\
            UPDATE settings
            SET voice_id = ?
            WHERE id = ?""", (voice_id, user_id))

        if volume is not None:
            c.execute("""\
            UPDATE settings
            SET volume = ?
            WHERE id = ?""", (volume, user_id))

        self.conn.commit()

    def delete_user(self, user_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM settings WHERE id=?", (user_id,))
        self.conn.commit()

    def get_user_settings(self, user_id):
        c = self.conn.cursor()

        c.execute("SELECT * FROM settings WHERE id=?", (user_id,))

        user = c.fetchone()

        if user is None:
            return None
        return dict(user_id=user[0], rate=user[1], voice_id=user[2], volume=user[3])

    def user_exists(self, user_id):
        c = self.conn.cursor()
        c.execute("SELECT 1 FROM settings WHERE id=?", (user_id,))
        return c.fetchone() is not None


if __name__ == '__main__':
    s = TTSSettings()
    print(s.user_exists(123))
