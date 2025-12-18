import logging

import graphene
from graphene import relay, String
from graphene_sqlalchemy import SQLAlchemyObjectType
from sqlalchemy import or_

from api.graphqlutils import FTSFilterableConnectionField, get_arg_val
from storage.sql import Item

logger = logging.getLogger(__name__)


class ItemType(SQLAlchemyObjectType):
    class Meta:
        model = Item
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    items = FTSFilterableConnectionField(
        ItemType,
        fts=dict(
            fields=[  # all these fields get the _like query
                "title",
                "url",
            ],
        ),
        q=String(),
    )
    item = relay.Node.Field(ItemType)

    def resolve_item(self, info, *args, **kwargs):
        flask_session = info.context.get("flask_session", {})
        is_admin = flask_session.get("admin") is True
        item_obj = Query.item.get_node(info, *args, **kwargs)
        if item_obj and (item_obj.hidden and not is_admin):
            return None
        return item_obj

    def resolve_items(self, info, *args, **kwargs):
        flask_session = info.context.get("flask_session", {})
        is_admin = flask_session.get("admin") is True
        logger.info(
            f"Items query by {flask_session.get('user') if is_admin else 'anonymous'}"
        )
        q = None
        re_arguments = []
        for argument in info.field_asts[0].arguments:
            if argument.name.value == "q":
                q = get_arg_val(argument, info)
            else:
                re_arguments.append(argument)
        # info.field_asts[0].arguments = re_arguments
        query = Query.items.get_query(Item, info)
        if not is_admin:
            query = query.filter(Item.hidden.is_(False))
        if q:
            fts_fields = ("title", "type", "url")
            logger.debug("FTS with like in {fts_fields}")
            query = query.filter(
                or_(*[getattr(Item, field).like(f"%{q}%") for field in fts_fields])
            )
        # add an artificial delay?
        # import time
        # time.sleep(2)
        return query


schema = graphene.Schema(query=Query, auto_camelcase=False)
