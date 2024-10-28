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


def test_base_model_has_on_create_hook() -> None:
    item_count = 0

    class MyModel(core.BaseModel):
        name: str

        def on_create(self) -> None:
            nonlocal item_count
            item_count += 1

    assert item_count == 0
    MyModel(name="foo")
    assert item_count == 1
    MyModel(name="bar")
    assert item_count == 2


def test_json_schema_to_model_basic_case() -> None:
    class MyModel(core.BaseModel):
        name: str
        age: int
        height: float
        is_active: bool

    expected = MyModel(name="foo", age=42, height=1.75, is_active=True)

    generated_model = core.json_schema_to_model(MyModel.model_json_schema())
    actual = generated_model(name="foo", age=42, height=1.75, is_active=True)
    assert actual.model_dump() == expected.model_dump()


def test_json_schema_to_model_with_base_model_specified() -> None:
    class MyId(core.Id): ...

    class MyModel(core.BaseUpdateTimeAwareModel, core.BaseEntity[MyId]):  # type: ignore[misc]
        name: str

    class MyModel2(MyModel):
        age: int
        height: float
        is_active: bool

    expected = MyModel2(
        id="01HVRQ0XMMDDRNKGAW2R19ZQNW",
        name="foo",
        age=42,
        height=1.75,
        is_active=True,
        created_at=1713415263253018,
        updated_at=1713415263253043,
    )

    generated_model = core.json_schema_to_model(MyModel2.model_json_schema(), base_model=MyModel)
    actual = generated_model(
        id="01HVRQ0XMMDDRNKGAW2R19ZQNW",
        name="foo",
        age=42,
        height=1.75,
        is_active=True,
        created_at=1713415263253018,
        updated_at=1713415263253043,
    )
    assert actual.model_dump() == expected.model_dump()


def test_json_schema_to_model_supports_array() -> None:
    class MyModel(core.BaseModel):
        items: Sequence[str]

    expected = MyModel(items=["foo", "bar", "baz"])
    generated_model = core.json_schema_to_model(MyModel.model_json_schema())
    actual = generated_model(items=["foo", "bar", "baz"])
    assert actual.model_dump() == expected.model_dump()


def test_json_schema_to_model_supports_nested_model() -> None:
    class UrlModel(core.BaseModel):
        value: str

    class MyNestedNestedModel(core.BaseModel):
        name: str
        age: int
        profile_url: UrlModel

    class MyNestedModel(core.BaseModel):
        obj: MyNestedNestedModel
        flag: bool

    class MyModel(core.BaseModel):
        nested: MyNestedModel
        reference_url: UrlModel

    expected = MyModel(
        nested=MyNestedModel(
            obj=MyNestedNestedModel(name="foo", age=42, profile_url=UrlModel(value="https://example.com")),
            flag=True,
        ),
        reference_url=UrlModel(value="http://localhost"),
    )

    generated_model = core.json_schema_to_model(MyModel.model_json_schema())
    actual = generated_model(
        nested={
            "obj": {"name": "foo", "age": 42, "profileUrl": {"value": "https://example.com"}},
            "flag": True,
        },
        referenceUrl={"value": "http://localhost"},
    )
    assert actual.model_dump() == expected.model_dump()


def test_json_schema_to_model_supports_array_nested_model() -> None:
    class NestedItem(core.BaseModel):
        name: str
        age: int

    class MyModel(core.BaseModel):
        data: Sequence[NestedItem]

    expected = MyModel(data=[NestedItem(name="foo", age=42), NestedItem(name="bar", age=99)])

    generated_model = core.json_schema_to_model(MyModel.model_json_schema())
    actual = generated_model(data=[{"name": "foo", "age": 42}, {"name": "bar", "age": 99}])
    assert actual.model_dump() == expected.model_dump()
    assert hasattr(actual, "data")
    assert isinstance(actual.data, list)
    assert actual.data[0].name == "foo"
    assert actual.data[0].age == 42
    assert actual.data[1].name == "bar"
    assert actual.data[1].age == 99


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
