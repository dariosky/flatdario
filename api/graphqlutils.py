import graphene
from graphene import NonNull, Argument, List
from graphene_sqlalchemy import SQLAlchemyConnectionField
from sqlalchemy import inspect


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
        model = type._meta.model
        filter_fields = {
            self.set_field_case(field_name): self.get_type(field_type)
            for field_name, field_type in type._meta.fields.items()
        }
        super().__init__(type, *args,
                         **filter_fields,
                         sort=Argument(List(sort_enum_for(model))),
                         **kwargs)

    @staticmethod
    def set_field_case(field_name):
        if field_name in {'type', 'sort'}:
            return field_name.upper()
        return field_name

    @staticmethod
    def get_type(field):
        result = field._type
        if isinstance(result, NonNull):
            result = result._of_type
        return Argument(result)

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


class FTSFilterableConnectionField(FilterableConnectionField):
    _fulltext_field_suffix = '__like'

    def __init__(self, type, *args, fts_fields=None, **kwargs):
        self.fts_fields = fts_fields

        filter_fields = {}
        self._fts_attributes = {}  # the attribute with it's fieldname
        for field_name in fts_fields or []:
            attr_name = field_name + self._fulltext_field_suffix
            attr_name = self.set_field_case(attr_name)
            field_type = type._meta.fields[field_name]
            filter_fields[attr_name] = self.get_type(field_type)
            self._fts_attributes[attr_name] = field_name

        super().__init__(type, *args, **filter_fields, **kwargs)

    @classmethod
    def get_query(cls, model, info, **kwargs):
        # for attr_name, fieldname in self._fts_attributes.items()
        fts_query = {}
        for attr_name in list(kwargs.keys()):
            if attr_name.endswith(cls._fulltext_field_suffix):
                field_name = attr_name[:-len(cls._fulltext_field_suffix)]
                fts_query[field_name] = kwargs.pop(attr_name)

        query = super().get_query(model, info, **kwargs)
        for field_name, value in fts_query.items():
            column = getattr(model, field_name)
            query = query.filter(column.like(f"%{value}%"))
        return query
