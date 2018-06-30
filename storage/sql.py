import datetime
import logging

import sqlalchemy
from flask import json
from sqlalchemy import (create_engine, Column, String,
                        DateTime, func, Integer)
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


class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    subscription_date = Column(DateTime, default=datetime.datetime.utcnow)
    user_agent = Column(String, nullable=True)
    subscription = Column(String, nullable=False)
    last_notification = Column(DateTime, nullable=True)
    invalidation_date = Column(DateTime, nullable=True)

    @property
    def min_date(self):
        return (self.last_notification
                or self.subscription_date
                or (datetime.datetime.now() - datetime.timedelta(days=1)))


class StorageSqliteDB(Storage):
    SQL_FIELDS = {'id', 'type', 'url', 'timestamp', 'title'}

    @staticmethod
    def item_from_db(dbitem):
        """ Return an item dictionary out of the DB one """
        item = {k: getattr(dbitem, k) for k in StorageSqliteDB.SQL_FIELDS}
        if dbitem.extra:
            extra_fields = json.loads(dbitem.extra)
            item.update(extra_fields)
        return item

    def all(self):
        items = []
        for dbitem in self.db.query(Item) \
            .order_by(sqlalchemy.desc(Item.timestamp)):
            item = self.item_from_db(dbitem)
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

    def getitem(self, item_id):
        dbitem = self.db.query(Item).get(item_id)
        return self.item_from_db(dbitem)

    def upsert(self, item, update=False):
        """ Write to SQL Item - move all extra fields in an extra json"""
        fields = {k: v for k, v in item.items()
                  if k in self.SQL_FIELDS}
        extra = {k: v for k, v in item.items()
                 if k not in self.SQL_FIELDS}
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

    def active_subscriptions(self):
        return list(
            self.db.query(Subscription)
                .filter(Subscription.invalidation_date.is_(None))
                .order_by(sqlalchemy.asc(Subscription.subscription_date))
        )

    def set_last_notification(self, subscription):
        """ Mark the time when the subscription got last notified """
        q = self.db.query(Subscription).filter(
            Subscription.subscription == subscription
        )
        subscription = q.first()
        subscription.last_notification = datetime.datetime.utcnow()
        self.db.commit()

    def invalidate_subscription(self, subscription):
        q = self.db.query(Subscription).filter(
            Subscription.subscription == subscription
        )
        subscription = q.first()
        subscription.invalidation_date = datetime.datetime.utcnow()
        self.db.commit()
