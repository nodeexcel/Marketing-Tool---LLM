import asyncio
from app.core.database import connect_db, get_database


async def main():
    await connect_db()
    db = get_database()
    doc = await db.prompt_library.find_one({"prompt_id": "default_competitor_intelligence"})
    if doc:
        print(f"OK    seeded in DB: agent_id={doc['agent_id']} category={doc['category']}")
    else:
        print("MISS  not in DB yet — will seed on next clean restart")


asyncio.run(main())
