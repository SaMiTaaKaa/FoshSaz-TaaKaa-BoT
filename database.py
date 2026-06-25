import asyncpg
import random
from config import DATABASE_URL

db = None


async def connect_db():
    global db

    db = await asyncpg.create_pool(DATABASE_URL)

    async with db.acquire() as conn:

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id SERIAL PRIMARY KEY,
            word TEXT NOT NULL,
            used BOOLEAN DEFAULT FALSE
        )
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS sudo_users (
            user_id BIGINT PRIMARY KEY
        )
        """)

    print("Database Connected")


async def add_words(words_list):
    async with db.acquire() as conn:

        for word in words_list:
            await conn.execute(
                "INSERT INTO words (word) VALUES ($1)",
                word
            )


async def get_words_count():
    async with db.acquire() as conn:

        return await conn.fetchval(
            "SELECT COUNT(*) FROM words"
        )


async def get_all_words():
    async with db.acquire() as conn:

        rows = await conn.fetch(
            "SELECT word FROM words ORDER BY id"
        )

        return [row["word"] for row in rows]


async def generate_sentence():

    async with db.acquire() as conn:

        rows = await conn.fetch(
            """
            SELECT id, word
            FROM words
            WHERE used = FALSE
            """
        )

        if not rows:

            await conn.execute(
                "UPDATE words SET used = FALSE"
            )

            rows = await conn.fetch(
                """
                SELECT id, word
                FROM words
                WHERE used = FALSE
                """
            )

        if not rows:
            return None

        random.shuffle(rows)

        count = min(
            len(rows),
            random.randint(5, 25)
        )

        selected = rows[:count]

        ids = [x["id"] for x in selected]
        words = [x["word"] for x in selected]

        await conn.execute(
            """
            UPDATE words
            SET used = TRUE
            WHERE id = ANY($1::int[])
            """,
            ids
        )

        lines = []

        for i in range(0, len(words), 5):
            lines.append(
                " ".join(words[i:i + 5])
            )

        return "\n".join(lines[:5])
    