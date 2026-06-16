import sqlite3
from datetime import datetime
import os


class DatabaseManager:

    def __init__(self, db_path="gallery.db"):
        appdata_dir = os.getenv('APPDATA')
        self.db_path = os.path.join(appdata_dir, "AutoTaggingGallery", db_path)
        self.create_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = (
            sqlite3.Row
        )
        return conn

    def create_tables(self):
        query_photos = """
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_name TEXT NOT NULL,
            stored_name TEXT UNIQUE NOT NULL,
            upload_date TEXT NOT NULL
        );
        """

        query_tags = """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name TEXT UNIQUE NOT NULL
        );
        """

        query_photo_tags = """
        CREATE TABLE IF NOT EXISTS photo_tags (
            photo_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (photo_id, tag_id),
            FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        );
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query_photos)
            cursor.execute(query_tags)
            cursor.execute(query_photo_tags)
            conn.commit()

    def add_photo(self, original_name, stored_name, tags):
        upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO photos (original_name, stored_name, upload_date)
                VALUES (?, ?, ?)
            """,
                (original_name, stored_name, upload_date),
            )
            photo_id = cursor.lastrowid

            for tag in tags:
                tag = tag.lower().strip()
                if not tag:
                    continue

                cursor.execute(
                    "INSERT OR IGNORE INTO tags (tag_name) VALUES (?)", (tag,)
                )

                cursor.execute(
                    "SELECT id FROM tags WHERE tag_name = ?", (tag,)
                )
                tag_id = cursor.fetchone()["id"]

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO photo_tags (photo_id, tag_id)
                    VALUES (?, ?)
                """,
                    (photo_id, tag_id),
                )

            conn.commit()
            return photo_id

        except sqlite3.Error as e:
            conn.rollback()
            raise sqlite3.Error(f"Database error while adding a photo: {e}")
        finally:
            conn.close()

    def get_photos_by_tag(self, tag_name):
        tag_name = tag_name.lower().strip()
        query = """
            SELECT p.id, p.original_name, p.stored_name, p.upload_date 
            FROM photos p
            JOIN photo_tags pt ON p.id = pt.photo_id
            JOIN tags t ON pt.tag_id = t.id
            WHERE t.tag_name LIKE ?
            ORDER BY p.id DESC
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (f"{tag_name}",))
            return [dict(row) for row in cursor.fetchall()]

    def get_tags_for_photo(self, filepath):
        stored_name = os.path.basename(filepath)
        query = """
            SELECT t.tag_name 
            FROM tags t
            JOIN photo_tags pt ON t.id = pt.tag_id
            JOIN photos p ON pt.photo_id = p.id
            WHERE p.stored_name = ?
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (stored_name,))
            return [row["tag_name"] for row in cursor.fetchall()]

    def get_all_photos(self):
        query = """
            SELECT id, original_name, stored_name, upload_date 
            FROM photos 
            ORDER BY id DESC
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def delete_photo(self, photo_id):
        query = "DELETE FROM photos WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (photo_id,))
            conn.commit()

    def get_original_name(self, filepath):
        stored_name = os.path.basename(filepath)
        query = "SELECT original_name FROM photos WHERE stored_name = ?"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (stored_name,))
            row = cursor.fetchone()
            return row["original_name"]