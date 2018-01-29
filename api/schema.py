import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from storage.sql import Item


class ItemType(SQLAlchemyObjectType):
    class Meta:
        model = Item
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_items = SQLAlchemyConnectionField(ItemType)


schema = graphene.Schema(query=Query)
