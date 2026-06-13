import aiosqlite
from datetime import datetime

DB_NAME = "database.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0,
            referrals INTEGER DEFAULT 0,
            referred_by INTEGER,
            captcha_passed INTEGER DEFAULT 0,
            created_at TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER,
            referred_id INTEGER UNIQUE,
            reward REAL DEFAULT 2.0,
            created_at TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS completed_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sponsor_link TEXT,
            reward REAL DEFAULT 0.3,
            completed_at TEXT,
            UNIQUE(user_id, sponsor_link)
        )
        """)

        await db.commit()


# ---------------- USERS ----------------

async def create_user(
    user_id: int,
    username: str = None,
    referred_by: int = None
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        INSERT OR IGNORE INTO users (
            user_id,
            username,
            referred_by,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """, (
            user_id,
            username,
            referred_by,
            datetime.utcnow().isoformat()
        ))

        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT *
        FROM users
        WHERE user_id = ?
        """, (user_id,))

        return await cursor.fetchone()


async def user_exists(user_id: int):
    user = await get_user(user_id)
    return user is not None


async def set_captcha_passed(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        UPDATE users
        SET captcha_passed = 1
        WHERE user_id = ?
        """, (user_id,))

        await db.commit()


async def captcha_passed(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT captcha_passed
        FROM users
        WHERE user_id = ?
        """, (user_id,))

        row = await cursor.fetchone()

        if not row:
            return False

        return bool(row[0])


# ---------------- BALANCE ----------------

async def get_balance(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT balance
        FROM users
        WHERE user_id = ?
        """, (user_id,))

        row = await cursor.fetchone()

        if not row:
            return 0

        return float(row[0])


async def add_balance(
    user_id: int,
    amount: float
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        UPDATE users
        SET balance = balance + ?
        WHERE user_id = ?
        """, (
            amount,
            user_id
        ))

        await db.commit()


async def subtract_balance(
    user_id: int,
    amount: float
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        UPDATE users
        SET balance = balance - ?
        WHERE user_id = ?
        """, (
            amount,
            user_id
        ))

        await db.commit()


# ---------------- REFERRALS ----------------

async def add_referral(
    referrer_id: int,
    referred_id: int
):
    async with aiosqlite.connect(DB_NAME) as db:

        try:

            await db.execute("""
            INSERT INTO referrals (
                referrer_id,
                referred_id,
                created_at
            )
            VALUES (?, ?, ?)
            """, (
                referrer_id,
                referred_id,
                datetime.utcnow().isoformat()
            ))

            await db.execute("""
            UPDATE users
            SET referrals = referrals + 1
            WHERE user_id = ?
            """, (referrer_id,))

            await db.commit()

            return True

        except Exception:
            return False


async def get_referrals_count(
    user_id: int
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT referrals
        FROM users
        WHERE user_id = ?
        """, (user_id,))

        row = await cursor.fetchone()

        if not row:
            return 0

        return row[0]


# ---------------- TASKS ----------------

async def task_completed(
    user_id: int,
    sponsor_link: str
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT id
        FROM completed_tasks
        WHERE user_id = ?
        AND sponsor_link = ?
        """, (
            user_id,
            sponsor_link
        ))

        row = await cursor.fetchone()

        return row is not None


async def save_completed_task(
    user_id: int,
    sponsor_link: str
):
    async with aiosqlite.connect(DB_NAME) as db:

        try:

            await db.execute("""
            INSERT INTO completed_tasks (
                user_id,
                sponsor_link,
                completed_at
            )
            VALUES (?, ?, ?)
            """, (
                user_id,
                sponsor_link,
                datetime.utcnow().isoformat()
            ))

            await db.commit()

            return True

        except Exception:
            return False


# ---------------- WITHDRAWALS ----------------

async def create_withdrawal(
    user_id: int,
    amount: float
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        INSERT INTO withdrawals (
            user_id,
            amount,
            created_at
        )
        VALUES (?, ?, ?)
        """, (
            user_id,
            amount,
            datetime.utcnow().isoformat()
        ))

        await db.commit()

        return cursor.lastrowid


async def get_user_withdrawals(
    user_id: int
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT *
        FROM withdrawals
        WHERE user_id = ?
        ORDER BY id DESC
        """, (user_id,))

        return await cursor.fetchall()

