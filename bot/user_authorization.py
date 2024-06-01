from pyrogram.client import Client
from config.config import settings
from config.proxy import proxy

user = Client("my_session", api_id=settings.API_ID, api_hash=settings.API_HASH, proxy=proxy)
