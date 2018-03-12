import graphene
from graphene import relay, Argument, List, NonNull
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


class FilterableConnectionField(SQLAlchemyConnectionField):
    """ An enhanced ConnectionField that adds 'sort' by any field
        and arguments in the SqlAlchemy columns for filtering
    """

    # see discussion on https://github.com/graphql-python/graphene-sqlalchemy/issues/27
    def __init__(self, type, *args, **kwargs):
        def set_field_case(field_name):
            if field_name in {'type', 'sort'}:
                return field_name.upper()
            return field_name

        def get_type(field):
            result = field._type
            if isinstance(result, NonNull):
                result = result._of_type
            return Argument(result)

        filter_fields = {
            set_field_case(field_name): get_type(field_type)
            for field_name, field_type in type._meta.fields.items()
        }
        super().__init__(type, *args,
                         **filter_fields,
                         sort=Argument(List(sort_enum_for(Item))),
                         **kwargs)

    # See: https://github.com/graphql-python/graphene-sqlalchemy/issues/27#issuecomment-341824371
    RELAY_ARGS = ['first', 'last', 'before', 'after']

    @classmethod
    def get_query(cls, model, info, **kwargs):
        sort = kwargs.pop('sort', None)
        query = super().get_query(model, info, **kwargs)

        for field, value in kwargs.items():
            if field not in FilterableConnectionField.RELAY_ARGS:
                query = query.filter(getattr(model, field.lower()) == value)

        if sort:
            query = query.order_by(*sort)
        return query


class Query(graphene.ObjectType):
    items = FilterableConnectionField(ItemType)
    item = relay.Node.Field(ItemType)


schema = graphene.Schema(query=Query)
