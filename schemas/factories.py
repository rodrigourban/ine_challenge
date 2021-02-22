import factory
from factory import fuzzy
from faker import Factory
from .models import Table, Attribute

faker = Factory.create()


class AttributeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attribute

    name = factory.LazyAttribute(lambda _: faker.word())
    attr_type = fuzzy.FuzzyChoice(
        ['str', 'int', 'bool', 'datetime', 'float']
    )


class TableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Table

    name = factory.LazyAttribute(lambda _: faker.word())
