import asyncio

from sqlalchemy import delete

from apps.football_pool.database import async_session_factory
from apps.football_pool.models import ChatMessage


async def clear_chat():
    async with async_session_factory() as session:
        result = await session.execute(delete(ChatMessage))
        await session.commit()
        print(f"Successfully cleared {result.rowcount} chat message(s).")


asyncio.run(clear_chat())
