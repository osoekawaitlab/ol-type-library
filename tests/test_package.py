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
