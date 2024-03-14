from datetime import datetime, timezone

from freezegun import freeze_time
from pytest_mock import MockerFixture
from ulid import ULID

from oltl import core


def test_id_generates_inherited_class_instance() -> None:
    class MyId(core.Id): ...

    actual = MyId.generate()
    assert isinstance(actual, MyId)
    assert isinstance(actual, core.Id)


def test_timestamp_now() -> None:
    dt = datetime(2024, 3, 14, 18, 52, 43, 123456, tzinfo=timezone.utc)
    with freeze_time(dt):
        actual = core.Timestamp.now()
    expected = core.Timestamp(dt)
    assert actual == expected


def test_derived_entity_has_derived_id(mocker: MockerFixture) -> None:
    mocker.patch(
        "oltl.core.ulid.new",
        side_effect=[
            ULID(b"\x01\x8e.\t\xa9\x06=\x9b\x0fK\xaa\xdc'\x01\xe0;"),
            ULID(b"\x01\x8e<s\x08\xc0\xef\xca\x93\xf1\x17xNB\xafa"),
        ],
    )

    class MyId(core.Id): ...

    class MyEntity(core.BaseEntity[MyId]):
        name: str

    actual = MyEntity(name="foo")
    expected = MyEntity(id=MyId("01HRQ0KA867PDGYJXAVGKG3R1V"), name="foo")
    assert actual == expected

    actual2 = MyEntity(name="bar")
    expected2 = MyEntity(id=MyId("01HRY76260XZ597W8QF1745BV1"), name="bar")
    assert actual2 == expected2


def test_derived_entity_serialize_deserialize() -> None:
    class MyId(core.Id): ...

    class MyEntity(core.BaseEntity[MyId]):
        entity_name: str

    entity = MyEntity(id=MyId("01HRQ0KA867PDGYJXAVGKG3R1V"), entity_name="foo")
    actual = entity.model_dump_json()
    serialize_expected = '{"id":"01HRQ0KA867PDGYJXAVGKG3R1V","entityName":"foo"}'
    assert actual == serialize_expected
    deserialize_expected = entity
    assert MyEntity.model_validate_json(actual) == deserialize_expected
