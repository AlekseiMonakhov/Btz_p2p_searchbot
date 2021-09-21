from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from data.config import URL

engine = create_async_engine(URL, echo=False)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
