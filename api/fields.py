from rest_framework import serializers


class EnumField(serializers.ChoiceField):
    def __init__(self, enum, **kwargs):
        self.enum = enum
        kwargs['choices'] = [(e.value, e) for e in enum]
        super(EnumField, self).__init__(**kwargs)

    def to_representation(self, obj):
        if hasattr(obj, 'value'):
            return obj.value
        return obj

    def to_internal_value(self, data):
        try:
            return self.enum[data]
        except KeyError:
            self.fail('invalid_choice', input=data)
