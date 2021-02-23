from django.db import models
from django.db.models import Q
from datetime import datetime


class DateTimeActiveModel(models.Model):
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TableManager(models.Manager):

    def create_table_with_attributes(self, name, attribute_list):
        table = Table(name=name)
        table.save()
        for attribute in attribute_list:
            new_attribute = Attribute(
                name=attribute.get('name'),
                required=attribute.get('required', False),
                unique=attribute.get('unique', False),
                attr_type=attribute.get('attr_type'),
                table=table
            )
            new_attribute.save()
        return table

    def validate_required(self, required_attrs, attribute_list):
        for attribute in required_attrs:
            if attribute[0] not in attribute_list.keys():  # Required
                raise ValueError(f"The attribute {attribute[0]} is required")

    def insert_data(self, table_id, attribute_list):
        required_attrs = Attribute.objects.filter(
            table=table_id, required=True).values_list('name')
        self.validate_required(required_attrs, attribute_list)
        for key, value in attribute_list.items():
            attribute = Attribute.objects.get(name=key, table=table_id)
            attribute.value = value
            attribute.save()

    def filter_by_attr(self, attribute_list):
        query_obj = Q()
        for name, value in attribute_list.items():
            query_obj = query_obj | Q(name=name, attr_value=value)

        attrs = Attribute.objects.filter(
            query_obj
        ).prefetch_related('table')

        return [attr.table for attr in attrs]


class Table(DateTimeActiveModel):
    name = models.CharField(max_length=100)
    related_tables = models.ManyToManyField(
        to="Table",
        related_name="related_schemas",
        blank=True
    )
    objects = TableManager()

    class Meta:
        ordering = ('created_at', )


class Attribute(DateTimeActiveModel):
    attr_type_choices = (
        ('str', 'String'),
        ('int', 'Integer'),
        ('float', 'Float'),
        ('datetime', 'Datetime'),
        ('bool', 'Boolean'),
    )
    name = models.CharField(max_length=100)
    attr_value = models.CharField(max_length=100, null=True)
    attr_type = models.CharField(
        choices=attr_type_choices,
        max_length=8,
        default='str'
    )
    unique = models.BooleanField(default=False)
    required = models.BooleanField(default=False)
    table = models.ForeignKey(
        to=Table,
        related_name="table_attrs",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

    def transform_value_type(self):
        if self.attr_value:
            if self.attr_type == 'int':
                return int(self.attr_value)
            elif self.attr_type == 'float':
                return float(self.attr_value)
            elif self.attr_type == 'bool':
                return True if self.attr_value == 'True' else False
            elif self.attr_type == 'datetime':
                return datetime.strptime(self.attr_value, '%d/%m/%Y')
            else:
                return self.attr_value

    @property
    def value(self):
        if self.attr_value:
            return self.transform_value_type()
        return self.attr_value

    @value.setter
    def value(self, new_value):
        if self.validate_attr_type(new_value):
            self.attr_value = str(new_value)
        else:
            raise ValueError(f"Attribute type for {self.name} does not match")

    def validate_attr_type(self, attribute):

        obj_type = str
        if self.attr_type == 'int':
            obj_type = int
        elif self.attr_type == 'float':
            obj_type = float
        elif self.attr_type == 'bool':
            obj_type = bool

        if self.attr_type == 'datetime':
            try:
                datetime.strptime(str(attribute), '%d/%m/%Y')
            except ValueError:
                obj_type = None

        return type(attribute) == obj_type
