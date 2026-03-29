"""Seed script: creates sample policies and users for testing."""
import asyncio
import sys
sys.path.insert(0, ".")

from src.models.database import init_db, get_session_factory
from src.models.policy import Policy
from src.models.user import UserIPConfig


async def seed():
    await init_db()
    factory = get_session_factory()

    async with factory() as session:
        # Create policies
        standard = Policy(name="Standard", default_ip_limit=2, reenable_delay_sec=300)
        premium = Policy(name="Premium", default_ip_limit=5, reenable_delay_sec=120)
        unlimited = Policy(name="Unlimited", default_ip_limit=999, notify_on_violation=False)

        session.add_all([standard, premium, unlimited])
        await session.flush()

        # Create sample users
        users = [
            UserIPConfig(username="demo_user1", policy_id=standard.id),
            UserIPConfig(username="demo_user2", policy_id=premium.id),
            UserIPConfig(username="demo_admin", policy_id=unlimited.id, is_exempt=True),
        ]
        session.add_all(users)
        await session.commit()

    print("Seed data created successfully.")
    print("Policies: Standard (2 IPs), Premium (5 IPs), Unlimited")
    print("Users: demo_user1, demo_user2, demo_admin")


if __name__ == "__main__":
    asyncio.run(seed())
