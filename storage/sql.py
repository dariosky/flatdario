import logging

from flask import json
from sqlalchemy import create_engine, Column, String, DateTime, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from collectors.exceptions import DuplicateFound
from storage import Storage

logger = logging.getLogger(__name__)

Base = declarative_base()


class Item(Base):
    __tablename__ = 'items'

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    url = Column(String)
    timestamp = Column(DateTime, nullable=False)
    title = Column(String, nullable=False)
    extra = Column(String)


class StorageSqliteDB(Storage):
    SQL_FIELDS = {'id', 'type', 'url', 'timestamp', 'title'}

    def all(self):
        pass

    def __init__(self, db_filename) -> None:
        super().__init__()
        engine = create_engine(f"sqlite:///{db_filename}",
                               # echo=True  # show the queries
                               )
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.db = Session()

    def search(self, id, type):
        pass

    def upsert(self, item, update=False):
        fields = {k: v for k, v in item.items() if k in self.SQL_FIELDS}
        extra = {k: v for k, v in item.items() if k not in self.SQL_FIELDS}
        new = Item(
            **fields,
            extra=json.dumps(extra)
        )
        if update:
            self.db.merge(new)
        else:
            self.db.add(new)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise DuplicateFound(
                f"We already have the id {item['id']} of type {item['type']} in the DB"
            )

    def max_timestamp(self, **kwargs):
        max_ts = self.db.query(func.max(Item.timestamp)).filter_by(**kwargs)
        return max_ts.one()[0]

    def close(self):
        self.db.close()
