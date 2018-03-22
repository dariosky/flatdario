import logging
import sqlalchemy

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
        items = []
        for dbitem in self.db.query(Item) \
            .order_by(sqlalchemy.desc(Item.timestamp)):
            item = {k: getattr(dbitem, k) for k in self.SQL_FIELDS}
            if dbitem.extra:
                extra_fields = json.loads(dbitem.extra)
                item.update(extra_fields)
            items.append(item)
        return items

    def __init__(self, db_filename) -> None:
        super().__init__()
        engine = create_engine(f"sqlite:///{db_filename}",
                               # echo=True  # show the queries
                               )
        Base.metadata.create_all(engine)
        # noinspection PyPep8Naming
        Session = sessionmaker(bind=engine)
        self.db = Session()

    def search(self, id, type):
        pass

    def upsert(self, item, update=False):
        fields = {k: v for k, v in item.items()
                  if k in self.SQL_FIELDS}
        extra = {k: v for k, v in item.items()
                 if k not in self.SQL_FIELDS and v}
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
        except IntegrityError as e:
            self.db.rollback()
            if "unique" in str(e.orig).lower():
                raise DuplicateFound(
                    f"We already have the id {item['id']} of type {item['type']} in the DB"
                )
            else:
                raise

    def max_timestamp(self, **kwargs):
        max_ts = self.db.query(func.max(Item.timestamp)).filter_by(**kwargs)
        return max_ts.one()[0]

    def close(self):
        self.db.close()
