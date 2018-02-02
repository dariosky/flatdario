import graphene
from graphene import relay, List
from graphene_sqlalchemy import SQLAlchemyObjectType

from storage.sql import Item


class ItemType(SQLAlchemyObjectType):
    class Meta:
        model = Item
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    items = List(ItemType, page=graphene.Int())
    item = relay.Node.Field(ItemType)

    def resolve_items(self, info, page=0):
        page_size = 10
        offset = page * page_size
        item_query = ItemType.get_query(info)
        return item_query.offset(offset).limit(page_size)


schema = graphene.Schema(query=Query)
