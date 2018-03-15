import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType

from api.graphqlutils import FTSFilterableConnectionField
from storage.sql import Item


class ItemType(SQLAlchemyObjectType):
    class Meta:
        model = Item
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    items = FTSFilterableConnectionField(ItemType, fts_fields=[
        'title', 'url'
    ])
    item = relay.Node.Field(ItemType)

    # def resolve_items(self, *args, **kwargs):
    #     import time
    #     time.sleep(50)


schema = graphene.Schema(query=Query)
