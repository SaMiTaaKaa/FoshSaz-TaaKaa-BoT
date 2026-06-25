import asyncpg
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

        count = await conn.fetchval(
            "SELECT COUNT(*) FROM words"
        )

        return count


async def get_all_words():
    async with db.acquire() as conn:

        rows = await conn.fetch(
            "SELECT word FROM words ORDER BY id"
        )

        return [row["word"] for row in rows]