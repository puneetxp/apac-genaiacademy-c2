"""Shared base for SLUSI CLI tools — loads config and instantiates services."""
from __future__ import annotations

import os
import sys

# Allow running tools directly without installing the package
_PYTHON_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PYTHON_DIR not in sys.path:
    sys.path.insert(0, _PYTHON_DIR)

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from app.services.shc_fetcher import SHCFetcher
from app.services.dss_parser import DSSParser
from app.services.shc_code_mapper import SHCCodeMapper


class SLUSIToolBase:
    """Loads config from env / .env file and instantiates shared service objects."""

    def __init__(self, env_file: str | None = None) -> None:
        load_dotenv(env_file or os.path.join(_PYTHON_DIR, ".env"))
        self._db_url: str | None = os.getenv("DATABASE_URL")
        self._engine: Engine | None = None

    # ------------------------------------------------------------------
    # Service accessors
    # ------------------------------------------------------------------

    def get_fetcher(self) -> SHCFetcher:
        return SHCFetcher()

    def get_parser(self) -> DSSParser:
        return DSSParser()

    def get_mapper(self) -> SHCCodeMapper:
        return SHCCodeMapper()

    # ------------------------------------------------------------------
    # DB (optional)
    # ------------------------------------------------------------------

    def get_db(self) -> Engine | None:
        """Return SQLAlchemy Engine, or None if DATABASE_URL is not set."""
        if self._db_url is None:
            return None
        if self._engine is None:
            self._engine = create_engine(self._db_url, pool_pre_ping=True)
        return self._engine

    def get_session(self) -> Session | None:
        """Return a new Session, or None if DATABASE_URL is not set."""
        engine = self.get_db()
        if engine is None:
            return None
        factory = sessionmaker(bind=engine)
        return factory()
