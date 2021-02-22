from rest_framework import serializers
from .models import Table, Attribute


class AttributeSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ('name', 'attr_type', 'unique', 'required')


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ('name', 'value')


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ('name')

    def to_representation(self, instance):
        attrs_qs = instance.table_attrs.all()
        serialized_data = [AttributeSerializer(attr).data for attr in attrs_qs]
        data = {
            attr['name']: attr['value'] for attr in serialized_data
        }
        data['name'] = instance.name
        return data


class TableSchemaSerializer(serializers.ModelSerializer):
    fields = serializers.JSONField(write_only=True)

    class Meta:
        model = Table
        fields = ('name', 'fields')

    def create(self, validated_data):
        return Table.objects.create_table_with_attributes(
            name=validated_data['name'],
            attribute_list=validated_data['fields']
        )

    def to_representation(self, instance):
        attrs_qs = instance.table_attrs.all()
        serializer = AttributeSchemaSerializer(attrs_qs, many=True).data
        return {
            'name': instance.name,
            'fields': serializer
        }
