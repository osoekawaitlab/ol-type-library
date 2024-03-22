import re

import oltl


def test_oltl_has_version() -> None:

    assert re.match(r"\d+\.\d+\.\d+", oltl.__version__)


def test_oltl_has_id() -> None:
    expected = "01HRQ0BNKS4WMFVQPW810MPM3V"
    actual = oltl.Id("01HRQ0BNKS4WMFVQPW810MPM3V")
    assert actual.str == expected


def test_oltl_has_timestamp() -> None:
    expected = 1627574400000000
    actual = oltl.Timestamp("2021-07-29T16:00:00Z")
    assert actual == expected


def test_oltl_has_base_model() -> None:
    class MyModel(oltl.BaseModel):
        object_name: str
        some_value: int

    actual = MyModel(object_name="foo", some_value=42)
    expected = '{"objectName":"foo","someValue":42}'
    assert actual.model_dump_json() == expected


def test_oltl_has_base_entity() -> None:
    class MyId(oltl.Id): ...

    class MyEntity(oltl.BaseEntity[MyId]):
        entity_name: str

    entity = MyEntity(id=MyId("01HRQ0KA867PDGYJXAVGKG3R1V"), entity_name="foo")
    actual = entity.model_dump_json()
    expected = '{"id":"01HRQ0KA867PDGYJXAVGKG3R1V","entityName":"foo"}'
    assert actual == expected
    assert MyEntity.model_validate_json(actual) == entity
