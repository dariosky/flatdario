from time import sleep

import graphene
from graphene import relay, Argument, List
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from sqlalchemy import inspect

from storage.sql import Item


class ItemType(SQLAlchemyObjectType):
    class Meta:
        model = Item
        interfaces = (relay.Node,)


def sort_enum_for(cls):
    """Create Graphene Enum for sorting a SQLAlchemy class query"""
    # https://github.com/graphql-python/graphene-sqlalchemy/issues/40
    name = cls.__name__ + 'SortEnum'
    items = []
    for attr in inspect(cls).attrs:
        try:
            asc = attr.expression
            desc = asc.desc()
        except AttributeError:
            pass
        else:
            key = attr.key.upper()
            items.extend([(key + '_ASC', asc), (key + '_DESC', desc)])
    return graphene.Enum(name, items)


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    items = SQLAlchemyConnectionField(ItemType,
                                      sort=Argument(List(sort_enum_for(Item))))
    item = relay.Node.Field(ItemType)

    search = graphene.List(ItemType, q=graphene.String())

    def resolve_search(self, info, q):
        item_query = ItemType.get_query(info)
        return item_query.filter(
            Item.type.contains(q)
            | Item.title.contains(q)
            # | Item.extra.contains(q)
        ).all()

    # if we don't want to use the ConnectionField but a list
    # we have to implement pagination by ourselves:

    def resolve_items(self, info, *args, sort=None, **kwargs, ):
        if sort is None:
            sort = ["timestamp desc", ]
        # sleep(5)
        query = ItemType.get_query(info)
        return query.order_by(*sort)

    # def resolve_items(self, info, page=0):
    #     page_size = 10
    #     offset = page * page_size
    #     item_query = ItemType.get_query(info)
    #     return item_query.offset(offset).limit(page_size)
    #


schema = graphene.Schema(query=Query)
