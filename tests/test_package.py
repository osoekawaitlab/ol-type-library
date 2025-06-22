import re

import oltl
from oltl import core


def test_oltl_has_version() -> None:

    assert re.match(r"\d+\.\d+\.\d+", oltl.__version__)


def test_oltl_has_id() -> None:
    assert oltl.Id == core.Id


def test_oltl_has_timestamp() -> None:
    assert oltl.Timestamp == core.Timestamp


def test_oltl_has_base_model() -> None:
    assert oltl.BaseModel == core.BaseModel


def test_oltl_has_base_entity() -> None:
    assert oltl.BaseEntity == core.BaseEntity


def test_oltl_has_base_creation_time_aware_model() -> None:
    assert oltl.BaseCreationTimeAwareModel == core.BaseCreationTimeAwareModel


def test_oltl_has_base_update_time_aware_model() -> None:
    assert oltl.BaseCreationTimeAwareModel == core.BaseCreationTimeAwareModel


def test_oltl_has_string_mixins() -> None:
    assert oltl.BaseString == core.BaseString
    assert oltl.LimitedMinLengthStringMixIn == core.LimitedMinLengthStringMixIn
    assert oltl.NonEmptyStringMixIn == core.NonEmptyStringMixIn
    assert oltl.LimitedMaxLengthStringMixIn == core.LimitedMaxLengthStringMixIn
    assert oltl.NormalizedStringMixIn == core.NormalizedStringMixIn
    assert oltl.RegexSubstitutedStringMixIn == core.RegexSubstitutedStringMixIn
    assert oltl.TrimmedStringMixIn == core.TrimmedStringMixIn
    assert oltl.SnakeCaseStringMixIn == core.SnakeCaseStringMixIn
    assert oltl.CamelCaseStringMixIn == core.CamelCaseStringMixIn
    assert oltl.RegexMatchedStringMixIn == core.RegexMatchedStringMixIn


def test_oltl_has_base_bytes() -> None:
    assert oltl.BaseBytes == core.BaseBytes


def test_oltl_has_json_schema_to_model() -> None:
    assert oltl.json_schema_to_model == core.json_schema_to_model


def test_oltl_has_integer_mixins() -> None:
    assert oltl.BaseInteger == core.BaseInteger
    assert oltl.LowerBoundIntegerMixIn == core.LowerBoundIntegerMixIn
    assert oltl.UpperBoundIntegerMixIn == core.UpperBoundIntegerMixIn


def test_oltl_has_float_mixins() -> None:
    assert oltl.BaseFloat == core.BaseFloat
    assert oltl.LowerBoundFloatMixIn == core.LowerBoundFloatMixIn
    assert oltl.UpperBoundFloatMixIn == core.UpperBoundFloatMixIn


def test_oltl_has_json_acceptable() -> None:
    assert oltl.JsonAcceptable == core.JsonAcceptable


def test_oltl_has_type_vars() -> None:
    assert oltl.StringT == core.StringT
    assert oltl.IntegerT == core.IntegerT
    assert oltl.FloatT == core.FloatT
    assert oltl.BytesT == core.BytesT
    assert oltl.IdT == core.IdT


def test_oltl_has_path_related_types() -> None:
    assert oltl.NewOrExistingFilePath == core.NewOrExistingFilePath
    assert oltl.NewOrExistingDirectoryPath == core.NewOrExistingDirectoryPath


from pydantic import AliasChoices, AliasGenerator, ConfigDict
from pydantic.alias_generators import to_camel

from oltl import BaseModel

to_reference = AliasGenerator(
    validation_alias=lambda field_name: AliasChoices(
        field_name, f"{field_name}_id", to_camel(field_name), to_camel(f"{field_name}_id")
    ),
    alias=lambda field_name: field_name,
    serialization_alias=lambda field_name: to_camel(field_name),
)


class A(BaseModel):
    id: oltl.Id
    name: str


class B(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_reference, validate_assignment=True)
    a: A


class C(BaseModel):
    name_object: str


def test_oltl_has_base_model() -> None:
    idstr = oltl.Id.generate().str
    c = C.model_validate({"name_object": "s"})
    assert c.name_object == "s"
    c = C.model_validate({"nameObject": "s"})
    assert c.name_object == "s"
    b = B.model_validate({"a": {"id": idstr, "name": "b"}})
    assert b.a.id == idstr
    assert b.a.name == "b"
    b = B.model_validate({"a_id": {"id": idstr, "name": "b"}})
    assert b.a.id == idstr
    assert b.a.name == "b"
