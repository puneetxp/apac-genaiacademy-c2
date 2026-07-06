import asyncio
import sys
from app.orm.user import User
from app.orm.active_role import ActiveRole
from app.core.database import get_db

async def main():
    result = ActiveRole.where({'user_id': [1]}).get()
    print("Result:", result.items if result else "None")

asyncio.run(main())
