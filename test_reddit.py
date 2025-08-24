import os, asyncio, asyncpraw
from dotenv import load_dotenv
load_dotenv()

async def main():
    reddit = asyncpraw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=f"script:macrocosm_clean:v1 (by u/{os.getenv('REDDIT_USERNAME')})",
    )
    try:
        me = await reddit.user.me()
        print("Authenticated as:", me.name)
    finally:
        await reddit.close()   # ВАЖНО

asyncio.run(main())
