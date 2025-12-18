import logging

import graphene
import sqlalchemy
from graphene import NonNull, Argument, List
from graphene_sqlalchemy import SQLAlchemyConnectionField
from graphql import ResolveInfo
from graphql.language.ast import Variable
from sqlalchemy import inspect

logger = logging.getLogger(__name__)


def sort_enum_for(cls):
    """Create Graphene Enum for sorting a SQLAlchemy class query"""
    # https://github.com/graphql-python/graphene-sqlalchemy/issues/40
    name = cls.__name__ + "SortEnum"
    items = []
    for attr in inspect(cls).attrs:
        try:
            asc = attr.expression
            desc = asc.desc()
        except AttributeError:
            pass
        else:
            key = attr.key.upper()
            items.extend([(key + "_ASC", asc), (key + "_DESC", desc)])
    return graphene.Enum(name, items)


class FilterableConnectionField(SQLAlchemyConnectionField):
    """An enhanced ConnectionField that adds 'sort' by any field
    and arguments in the SqlAlchemy columns for filtering
    """

    # see discussion on https://github.com/graphql-python/graphene-sqlalchemy/issues/27
    def __init__(self, type, *args, **kwargs):
        model = type._meta.model
        filter_fields = {
            self.set_field_case(field_name): self.get_type(field_type)
            for field_name, field_type in type._meta.fields.items()
        }
        super().__init__(
            type,
            *args,
            **filter_fields,
            sort=Argument(List(sort_enum_for(model))),
            **kwargs,
        )

    @staticmethod
    def set_field_case(field_name):
        if field_name in {"type", "sort"}:
            return field_name.upper()
        return field_name

    @staticmethod
    def get_type(field):
        result = field._type
        if isinstance(result, NonNull):
            result = result._of_type
        return Argument(result)

    # See: https://github.com/graphql-python/graphene-sqlalchemy/issues/27#issuecomment-341824371
    RELAY_ARGS = ["first", "last", "before", "after"]

    @classmethod
    def get_query(cls, model, info, **kwargs):
        query = super().get_query(model, info, **kwargs)

        attrs = info_to_kwargs(info)
        for field, value in attrs.items():
            if field == "sort":
                order_field = get_arg_val(value, info).lower()

                if order_field.endswith("_desc"):
                    order_field = order_field[:-5]
                    order = sqlalchemy.desc(order_field)
                else:
                    order = order_field
                logger.debug("Sorting by %s" % order)
                query = query.order_by(order)
            elif field not in FilterableConnectionField.RELAY_ARGS:
                model_field = getattr(model, field.lower(), None)
                if model_field:
                    sql_value = get_arg_val(value, info)
                    logger.debug(f"Filter {model_field} == {sql_value}")
                    query = query.filter(model_field == sql_value)

        return query


class FTSFilterableConnectionField(FilterableConnectionField):
    _fulltext_field_suffix = "__like"

    def __init__(self, type, *args, fts=None, **kwargs):
        # add the *__like additional arguments to the schema
        self.fts = fts
        filter_fields = {}
        self._fts_attributes = {}  # the attribute with it's fieldname
        for field_name in fts["fields"] or []:
            attr_name = field_name + self._fulltext_field_suffix
            attr_name = self.set_field_case(attr_name)
            field_type = type._meta.fields[field_name]
            filter_fields[attr_name] = self.get_type(field_type)
            self._fts_attributes[attr_name] = field_name
        super().__init__(type, *args, **filter_fields, **kwargs)

    @classmethod
    def get_query(cls, model, info, **kwargs):
        # for attr_name, fieldname in self._fts_attributes.items()
        query = super().get_query(model, info, **kwargs)

        attrs = info_to_kwargs(info)
        for attr_name, value in attrs.items():
            if attr_name.lower().endswith(
                cls._fulltext_field_suffix
            ):  # when they ends in __like
                field_name = attr_name[: -len(cls._fulltext_field_suffix)]
                logger.debug(f"Filter field {field_name} like {value}")
                column = getattr(model, field_name)
                query = query.filter(column.like(f"%{value.value}%"))

        return query


def info_to_kwargs(info):
    return {
        argument.name.value: argument.value for argument in info.field_asts[0].arguments
    }


def get_arg_val(arg, info: ResolveInfo):
    result = arg
    if hasattr(result, "value"):
        result = arg.value
    if isinstance(result, Variable):
        variable_name = result.name.value
        return info.variable_values.get(variable_name)
    if hasattr(result, "value"):
        return result.value
    else:
        return result
