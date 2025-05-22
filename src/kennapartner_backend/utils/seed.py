from kennapartner_backend.modules import User
from kennapartner_backend.utils import connect_to_database
import bcrypt
import asyncio
from datetime import timezone, datetime
from kennapartner_backend.utils import logger


async def seed_user():
    await connect_to_database()

    users = await User.insert_many(
        [
            User(
                username="kenna_admin_123",
                password=bcrypt.hashpw(
                    "secure_pass_123".encode("utf-8"), bcrypt.gensalt()
                ),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
            User(
                username="kenna_admin_456",
                password=bcrypt.hashpw(
                    "secure_pass_456".encode("utf-8"), bcrypt.gensalt()
                ),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        ]
    )
    return users


def main():
    asyncio.run(seed_user())


if __name__ == "__main__":
    main()
