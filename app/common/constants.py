from enum import EnumMeta, IntEnum


def get_key_by_value(enum, value):
    for k, v in enum.__members__.iteritems():
        if v.value == value:
            return k


class IntEnumMixin(IntEnum):
    @classmethod
    def get_all_values(cls, not_in=None, join_items=None):
        if isinstance(not_in, (list, tuple)) and not_in:
            result = [each.value for each in cls.__members__.values() if each.value not in not_in]
        else:
            result = [each.value for each in cls.__members__.values()]
        if join_items and isinstance(join_items, list):
            result += join_items
        return result

    @classmethod
    def get_all_keys(cls):
        return cls.__members__.keys()

    @classmethod
    def get_all_values_string_format(cls, join_word=',', not_in=None, join_items=None):
        return join_word.join(map(str, cls.get_all_values(not_in, join_items)))

    @classmethod
    def get_name_by_value(cls, value):
        if isinstance(cls, EnumMeta):
            for k, v in cls.__members__.items():
                if isinstance(v, (tuple, list, dict)):
                    if value in v:
                        return k
                else:
                    if v == value:
                        return k

    @classmethod
    def get_name(cls):
        if isinstance(cls, EnumMeta):
            return cls._member_names_

    @classmethod
    def get_name_string_format(cls, join_word=','):
        if isinstance(cls, EnumMeta):
            return join_word.join(cls._member_names_)
