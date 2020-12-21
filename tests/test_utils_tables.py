import pytest

from bottex2.helpers import tables as t


@pytest.fixture
def cls():
    class Test(t.Table):
        a = t.Column()
        b = t.Column(primary=True)

        __values__ = (
            (1, '1'),
            (2, '2'),
            (3, '3')
        )
    return Test


def test_inheritance():
    class Base(t.Table):
        a = t.Column()
        b = t.Column()

    class Concrete(Base):
        __values__ = (
            (1, 'a'),
        )

    assert Concrete.columns == Base.columns


def test_column_descriptor(cls):
    assert isinstance(cls.a, t.Column)


def test_column_all(cls):
    assert cls.a.all() == [1, 2, 3]
    assert cls.b.all() == ['1', '2', '3']


def test_column_get(cls):
    with pytest.raises(KeyError):
        obj = cls.a[99]
    with pytest.raises(KeyError):
        obj = cls.a['a']

    obj = cls.a[1]
    assert isinstance(obj, cls)


def test_primary_column(cls):
    assert cls.primary_column.index == 1
    assert cls['3'] is cls.primary_column['3']


def test_instance(cls):
    obj = cls.a[1]
    assert isinstance(obj, cls)
    assert obj.a == 1 and obj.b == '1'
    assert list(obj.values) == [1, '1']
    assert list(obj) == [1, '1']
    assert obj.primary_value == '1'


def test_class(cls):
    assert len(cls) == 3
    assert list(cls) == cls.objects
    obj = cls.objects[0]
    assert isinstance(obj, cls)


if __name__ == '__main__':
    pytest.main()
