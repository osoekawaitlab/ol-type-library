import re
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Tuple, TypeAlias, Union

import pytest
from freezegun import freeze_time
from pydantic import ValidationError
from pytest_mock import MockerFixture
from ulid import ULID

from oltl import core

from .fixtures import string_test_cases


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


@pytest.mark.parametrize(argnames=["sut", "test_cases"], argvalues=string_test_cases)
def test_string_mixins(sut: TypeAlias, test_cases: Sequence[Tuple[str, Union[ValueError, str]]]) -> None:

    class TestModel(core.BaseModel):
        value: sut

    for test_case, expected in test_cases:
        if isinstance(expected, Exception):
            with pytest.raises(expected.__class__, match=re.escape(expected.__str__())):
                TestModel(value=test_case)
        else:
            actual = TestModel(value=test_case)
            assert actual.value == expected


def test_entity_id_is_immutable() -> None:
    class MyId(core.Id): ...

    class MyEntity(core.BaseEntity[MyId]):
        name: str

    entity = MyEntity(id=MyId("01HRQ0KA867PDGYJXAVGKG3R1V"), name="foo")
    with pytest.raises(ValidationError, match="1 validation error for MyEntity\nid\n\\s+Field is frozen.*"):
        entity.id = MyId("01HRQ0KA867PDGYJXAVGKG3R1V")


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


def test_creation_time_aware_model_has_created_at() -> None:
    class MyModel(core.BaseCreationTimeAwareModel):
        object_name: str
        some_value: int

    dt = datetime(2024, 3, 15, 23, 31, 21, 123456, tzinfo=timezone.utc)
    with freeze_time(dt):
        actual = MyModel(object_name="foo", some_value=42)
    expected = MyModel(created_at=core.Timestamp(dt), object_name="foo", some_value=42)
    assert actual == expected

    dt2 = datetime(2024, 3, 15, 23, 33, 15, 123456, tzinfo=timezone.utc)
    with freeze_time(dt2):
        actual2 = MyModel(object_name="bar", some_value=99)
    expected2 = MyModel(created_at=core.Timestamp(dt2), object_name="bar", some_value=99)
    assert actual2 == expected2


def test_created_at_is_immutable() -> None:
    class MyModel(core.BaseCreationTimeAwareModel):
        object_name: str
        some_value: int

    dt = datetime(2024, 3, 15, 23, 31, 21, 123456, tzinfo=timezone.utc)
    with freeze_time(dt):
        model = MyModel(object_name="foo", some_value=42)
    with pytest.raises(ValidationError, match="1 validation error for MyModel\ncreated_at\n\\s+Field is frozen.*"):
        model.created_at = core.Timestamp.now()


def test_creation_time_aware_model_seralize_deserialize() -> None:
    class MyModel(core.BaseCreationTimeAwareModel):
        object_name: str
        some_value: int

    dt = datetime(2024, 3, 15, 23, 31, 21, 123456, tzinfo=timezone.utc)
    with freeze_time(dt):
        model = MyModel(object_name="foo", some_value=42)
    actual = model.model_dump_json()
    serialize_expected = '{"createdAt":1710545481123456,"objectName":"foo","someValue":42}'
    assert actual == serialize_expected
    deserialize_expected = model
    assert MyModel.model_validate_json(actual) == deserialize_expected


def test_update_time_aware_model_has_created_at_and_updated_at() -> None:
    class MyModel(core.BaseUpdateTimeAwareModel):
        object_name: str
        some_value: int

    dt = datetime(2024, 3, 15, 23, 31, 21, 123456, tzinfo=timezone.utc)
    with freeze_time(dt):
        actual = MyModel(object_name="foo", some_value=42)
    expected = MyModel(created_at=core.Timestamp(dt), updated_at=core.Timestamp(dt), object_name="foo", some_value=42)
    assert actual == expected

    dt2 = datetime(2024, 3, 15, 23, 33, 15, 123456, tzinfo=timezone.utc)
    with freeze_time(dt2):
        actual.object_name = "bar"
    expected2 = MyModel(created_at=core.Timestamp(dt), updated_at=core.Timestamp(dt2), object_name="bar", some_value=42)
    assert actual == expected2


def test_updated_at_is_not_immutable() -> None:
    class MyModel(core.BaseUpdateTimeAwareModel):
        object_name: str
        some_value: int

    dt = datetime(2024, 3, 15, 23, 31, 21, 123456, tzinfo=timezone.utc)
    with freeze_time(dt):
        model = MyModel(object_name="foo", some_value=42)
    dt2 = datetime(2024, 3, 15, 23, 33, 15, 123456, tzinfo=timezone.utc)
    model.updated_at = core.Timestamp(dt2)
    expected = MyModel(created_at=core.Timestamp(dt), updated_at=core.Timestamp(dt2), object_name="foo", some_value=42)
    assert model == expected


def test_setattribute_error_doesnt_renew_updated_at() -> None:
    class MyModel(core.BaseUpdateTimeAwareModel):
        object_name: str
        some_value: int

    dt = datetime(2024, 3, 15, 23, 31, 21, 123456, tzinfo=timezone.utc)
    with freeze_time(dt):
        model = MyModel(object_name="foo", some_value=42)
    with pytest.raises(Exception):
        model.created_at = core.Timestamp.now()
    expected = MyModel(created_at=core.Timestamp(dt), updated_at=core.Timestamp(dt), object_name="foo", some_value=42)
    assert model == expected


def test_update_time_aware_model_serialize_deserialize() -> None:
    class MyModel(core.BaseUpdateTimeAwareModel):
        object_name: str
        some_value: int

    dt = datetime(2024, 3, 15, 23, 31, 21, 123456, tzinfo=timezone.utc)
    with freeze_time(dt):
        model = MyModel(object_name="foo", some_value=42)
    actual = model.model_dump_json()
    serialize_expected = '{"createdAt":1710545481123456,"updatedAt":1710545481123456,"objectName":"foo","someValue":42}'
    assert actual == serialize_expected
    deserialize_expected = model
    assert MyModel.model_validate_json(actual) == deserialize_expected
