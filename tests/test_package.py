import re

import oltl
from oltl import core


def test_oltl_has_version() -> None:

    assert re.match(r"\d+\.\d+\.\d+", oltl.__version__)


def test_oltl_has_id() -> None:
    oltl.Id == core.Id


def test_oltl_has_timestamp() -> None:
    oltl.Timestamp == core.Timestamp


def test_oltl_has_base_model() -> None:
    oltl.BaseModel == core.BaseModel


def test_oltl_has_base_entity() -> None:
    oltl.BaseEntity == core.BaseEntity


def test_oltl_has_base_creation_time_aware_model() -> None:
    oltl.BaseCreationTimeAwareModel == core.BaseCreationTimeAwareModel


def test_oltl_has_base_update_time_aware_model() -> None:
    oltl.BaseCreationTimeAwareModel == core.BaseCreationTimeAwareModel


def test_oltl_has_string_mixins() -> None:
    oltl.BaseString == core.BaseString
    oltl.LimitedMinLengthMixIn == core.LimitedMinLengthMixIn
    oltl.NonEmptyStringMixIn == core.NonEmptyStringMixIn
    oltl.LimitedMaxLengthMixIn == core.LimitedMaxLengthMixIn
    oltl.NormalizedStringMixIn == core.NormalizedStringMixIn
    oltl.RegexSubstitutedStringMixIn == core.RegexSubstitutedStringMixIn
    oltl.TrimmedStringMixIn == core.TrimmedStringMixIn
    oltl.SnakeCaseStringMixIn == core.SnakeCaseStringMixIn
    oltl.CamelCaseStringMixIn == core.CamelCaseStringMixIn
    oltl.RegexMatchedStringMixIn == core.RegexMatchedStringMixIn
