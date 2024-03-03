from contextlib import AbstractContextManager, asynccontextmanager

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apps.src.db_service.entities import Base


class DatabaseManager:
    """
    DatabaseManager class for managing asynchronous database operations
    using SQLAlchemy.
    """

    _initialized = False
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_url: str):
        """Initializes the Database instance with the provided database URL."""
        self._async_engine = create_async_engine(db_url, poolclass=NullPool)
        self._async_session_factory = async_sessionmaker(
            bind=self._async_engine, autoflush=False, expire_on_commit=False
        )

    async def delete_and_create_database(self) -> None:
        """Firstly delete and then create database tables based on SQLAlchemy
        Base metadata."""
        if not DatabaseManager._initialized:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)

            DatabaseManager._initialized = True

    async def delete_data_from_tables(self) -> None:
        if DatabaseManager._initialized:
            async with self._async_session_factory() as session:
                for table in reversed(Base.metadata.sorted_tables):
                    await session.execute(table.delete())
                await session.commit()

    @property
    def get_session_factory(self):
        """Getter for the asynchronous session factory."""
        return self._async_session_factory

    @asynccontextmanager
    async def session_cm(self) -> AbstractContextManager[AsyncSession]:
        """Context manager for handling database sessions."""
        session: AsyncSession = self._async_session_factory()
        try:
            yield session
        except Exception:
            # logger.exception("Session rollback because of exception")
            await session.rollback()
            raise
        finally:
            await session.close()
