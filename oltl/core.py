import re
from base64 import standard_b64decode, standard_b64encode
from datetime import datetime as _datetime
from datetime import timezone as _timezone
from typing import Any, Generic, Type, TypeAlias, TypeVar, Union, cast

import ulid
from dateutil.parser import parse as parse_datetime
from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    ConfigDict,
    Field,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    TypeAdapter,
)
from pydantic.alias_generators import to_camel, to_snake
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from ulid import ULID

from .utils import normalize_jptext

StrT = TypeVar("StrT", bound="BaseString")
BytesT = TypeVar("BytesT", bound="BaseBytes")
IdT = TypeVar("IdT", bound="Id")
IncEx: TypeAlias = "set[int] | set[str] | dict[int, IncEx] | dict[str, IncEx] | None"


class BaseBytes(bytes):
    """
    BaseBytes is a bytes type that can be used to validate and serialize bytes.

    >>> BaseBytes(b"test")
    BaseBytes(b'test')
    >>> bytes(BaseBytes(b"test"))
    b'test'
    >>> BaseBytes("YSAgMC1yMzJm")
    BaseBytes(b'a  0-r32f')
    >>> class TestBytes(BaseModel):
    ...   value: BaseBytes
    >>> TestBytes(value=b"test").model_dump()
    {'value': BaseBytes(b'test')}
    >>> TestBytes.model_validate_json('{"value":"YSAgMC1yMzJm"}')
    TestBytes(value=BaseBytes(b'a  0-r32f'))
    >>> TestBytes(value="YSAgMC1yMzJm").model_dump()
    {'value': BaseBytes(b'a  0-r32f')}
    >>> TestBytes(value=b"test").model_dump_json()
    '{"value":"dGVzdA=="}'
    >>> TestBytes.model_json_schema()
    {'properties': {'value': {'format': 'base64EncodedString', 'title': 'Value', 'type': 'string'}}, 'required': ['value'], 'title': 'TestBytes', 'type': 'object'}
    """  # noqa: E501

    def __new__(cls, value: Union[bytes, str]) -> "BaseBytes":
        if isinstance(value, bytes):
            return super(BaseBytes, cls).__new__(cls, value)
        return super(BaseBytes, cls).__new__(cls, standard_b64decode(value))

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.plain_serializer_function_ser_schema(cls.serialize, when_used="json"),
        )

    @classmethod
    def validate(cls: Type[BytesT], value: Any) -> BytesT:
        if isinstance(value, cls):
            return value
        if isinstance(value, (bytes, str)):
            return cls(value)
        raise ValueError(f"Cannot convert {value} to {cls.__name__}")

    def serialize(self) -> str:
        return standard_b64encode(self).decode()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __get_pydantic_json_schema__(self, _handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"format": "base64EncodedString", "type": "string"}


class BaseString(str):
    """
    BaseString is a string type that can be used to validate and serialize strings.

    >>> BaseString("test")
    BaseString('test')
    >>> str(BaseString("test"))
    'test'
    >>> ta = TypeAdapter(BaseString)
    >>> ta.validate_python("test")
    BaseString('test')
    >>> ta.validate_python(1)
    Traceback (most recent call last):
     ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for function-after[BaseString(), function-before[_proc_str(), str]]
      Input should be a valid string [type=string_type, input_value=1, input_type=int]
     ...
    >>> ta.dump_json(BaseString("test_test"))
    b'"test_test"'
    >>> BaseString.from_str("test")
    BaseString('test')
    >>> ta.validate_python(BaseString.from_str("test"))
    BaseString('test')
    >>> hash(BaseString("test")) == hash("test")
    True
    >>> ta.validate_python("test　test")
    BaseString('test　test')
    """  # noqa: E501

    @classmethod
    def _proc_str(cls, s: str) -> str:
        return s

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __str__(self) -> str:
        return super(BaseString, self).__str__()

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.no_info_before_validator_function(
                cls._proc_str, core_schema.str_schema(**cls.__get_extra_constraint_dict__())
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(cls.serialize, when_used="json"),
        )

    def serialize(self) -> str:
        return str(self)

    @classmethod
    def __get_extra_constraint_dict__(cls) -> dict[str, Any]:
        return {}

    def __hash__(self) -> int:
        return super(BaseString, self).__hash__()

    @classmethod
    def from_str(cls: Type[StrT], v: str) -> StrT:
        return TypeAdapter(cls).validate_python(v)


class LimitedMinLengthMixIn(BaseString):
    """
    LimitedMinLengthMixIn is a string type that can be used to validate and serialize strings with a minimum length.

    >>> class TestString(LimitedMinLengthMixIn, BaseString):
    ...   @classmethod
    ...   def get_min_length(cls) -> int:
    ...     return 3
    >>> TestString("test")
    TestString('test')
    >>> ta = TypeAdapter(TestString)
    >>> ta.validate_python("test")
    TestString('test')
    >>> ta.validate_python("te")
    Traceback (most recent call last):
     ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for function-after[TestString(), function-before[_proc_str(), constrained-str]]
      String should have at least 3 characters [type=string_too_short, input_value='te', input_type=str]
     ...
    >>> ta.validate_python("t")
    Traceback (most recent call last):
     ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for function-after[TestString(), function-before[_proc_str(), constrained-str]]
      String should have at least 3 characters [type=string_too_short, input_value='t', input_type=str]
     ...
    """  # noqa: E501

    @classmethod
    def get_min_length(cls) -> int:
        raise NotImplementedError

    @classmethod
    def __get_extra_constraint_dict__(cls) -> dict[str, Any]:
        return super().__get_extra_constraint_dict__() | {"min_length": cls.get_min_length()}


class NonEmptyStringMixIn(LimitedMinLengthMixIn, metaclass=type):
    """
    NonEmptyString is a string type that can be used to validate and serialize non-empty strings.
    >>> class NonEmptyString(NonEmptyStringMixIn):
    ...   ...
    >>> NonEmptyString.from_str("test")
    NonEmptyString('test')
    >>> ta = TypeAdapter(NonEmptyString)
    >>> ta.validate_python("test")
    NonEmptyString('test')
    >>> ta.validate_python("")
    Traceback (most recent call last):
     ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for function-after[NonEmptyString(), function-before[_proc_str(), constrained-str]]
      String should have at least 1 character [type=string_too_short, input_value='', input_type=str]
     ...
    """  # noqa: E501

    @classmethod
    def get_min_length(cls) -> int:
        return 1


class LimitedMaxLengthMixIn(BaseString):
    """
    LimitedMaxLengthMixIn is a string type that can be used to validate and serialize strings with a maximum length.

    >>> class TestString(LimitedMaxLengthMixIn, BaseString):
    ...   @classmethod
    ...   def get_max_length(cls) -> int:
    ...     return 3
    >>> TestString("test")
    TestString('test')
    >>> ta = TypeAdapter(TestString)
    >>> ta.validate_python("test")
    Traceback (most recent call last):
     ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for function-after[TestString(), function-before[_proc_str(), constrained-str]]
      String should have at most 3 characters [type=string_too_long, input_value='test', input_type=str]
     ...
    >>> ta.validate_python("te")
    TestString('te')
    """  # noqa: E501

    @classmethod
    def get_max_length(cls) -> int:
        raise NotImplementedError

    @classmethod
    def __get_extra_constraint_dict__(cls) -> dict[str, Any]:
        return super().__get_extra_constraint_dict__() | {"max_length": cls.get_max_length()}


class NormalizedStringMixIn(BaseString):
    """
    NormalizedStringMixIn is a string type that can be used to validate and serialize normalized strings.

    >>> class TestString(NormalizedStringMixIn, BaseString):
    ...   ...
    >>> TestString("test")
    TestString('test')
    >>> ta = TypeAdapter(TestString)
    >>> ta.validate_python("test")
    TestString('test')
    >>> ta.validate_python("test　test")
    TestString('test test')
    """

    @classmethod
    def _proc_str(cls, s: str) -> str:
        return super()._proc_str(normalize_jptext(s))


class RegexSubstitutedStringMixIn(BaseString):
    r"""
    RegexSubstitutedStringMixIn is a string type that substitute strings by regular expression.

    >>> class TestString(RegexSubstitutedStringMixIn, BaseString):
    ...   @classmethod
    ...   def get_pattern(cls) -> str:
    ...     return r"[\n\r]"
    ...   @classmethod
    ...   def get_repl(cls) -> str:
    ...     return " "
    >>> TestString.from_str("test\ntest")
    TestString('test test')
    """

    @classmethod
    def get_pattern(cls) -> str:
        raise NotImplementedError

    @classmethod
    def get_repl(cls) -> str:
        raise NotImplementedError

    @classmethod
    def _proc_str(cls, s: str) -> str:
        return super()._proc_str(re.sub(cls.get_pattern(), cls.get_repl(), s))


class RegexMatchedStringMixIn(BaseString):
    r"""
    RegexMatchedStringMixIn is a string type that can be used to validate and serialize strings matched by regular expression.

    >>> class TestString(RegexMatchedStringMixIn, BaseString):
    ...   @classmethod
    ...   def get_pattern(cls) -> str:
    ...     return r"^[a-z]+$"
    >>> TestString("test")
    TestString('test')
    >>> ta = TypeAdapter(TestString)
    >>> ta.validate_python("test")
    TestString('test')
    >>> ta.validate_python("test_test")
    Traceback (most recent call last):
     ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for function-after[TestString(), function-before[_proc_str(), constrained-str]]
      String should match pattern '^[a-z]+$' [type=string_pattern_mismatch, input_value='test_test', input_type=str]
     ...
    """  # noqa: E501

    @classmethod
    def get_pattern(cls) -> str:
        raise NotImplementedError

    @classmethod
    def __get_extra_constraint_dict__(cls) -> dict[str, Any]:
        return super().__get_extra_constraint_dict__() | {"pattern": cls.get_pattern()}


class TrimmedStringMixIn(BaseString):
    """
    TrimmedStringMixIn is a string type that can be used to validate and serialize trimmed strings.

    >>> class TestString(TrimmedStringMixIn, BaseString):
    ...   ...
    >>> TestString("test")
    TestString('test')
    >>> ta = TypeAdapter(TestString)
    >>> ta.validate_python("test")
    TestString('test')
    >>> ta.validate_python(" test ")
    TestString('test')
    """

    @classmethod
    def __get_extra_constraint_dict__(cls) -> dict[str, Any]:
        return super().__get_extra_constraint_dict__() | {"strip_whitespace": True}


class SnakeCaseStringMixIn(BaseString):
    """
    SnakeCaseStringMixIn is a string type that can be used to validate and serialize snake_case strings.

    >>> class TestString(SnakeCaseStringMixIn, BaseString):
    ...   ...
    >>> TestString("test")
    TestString('test')
    >>> ta = TypeAdapter(TestString)
    >>> ta.validate_python("test")
    TestString('test')
    >>> ta.validate_python("test_test")
    TestString('test_test')
    >>> ta.validate_python("testTest")
    TestString('test_test')
    """

    @classmethod
    def _proc_str(cls, s: str) -> str:
        return super()._proc_str(to_snake(s))


class CamelCaseStringMixIn(BaseString):
    """
    CamelCaseStringMixIn is a string type that can be used to validate and serialize camelCase strings.

    >>> class TestString(CamelCaseStringMixIn, BaseString):
    ...   ...
    >>> TestString("test")
    TestString('test')
    >>> ta = TypeAdapter(TestString)
    >>> ta.validate_python("test")
    TestString('test')
    >>> ta.validate_python("test_test")
    TestString('testTest')
    >>> ta.validate_python("alreadyCamelCasedWillBeLowerCased")
    TestString('alreadycamelcasedwillbelowercased')
    """

    @classmethod
    def _proc_str(cls, s: str) -> str:
        return super()._proc_str(to_camel(s))


class Id(ULID):
    r"""Id is a string type that can be used to validate and serialize ULID strings.

    >>> Id(ulid.from_int(1))
    Id('00000000000000000000000001')
    >>> Id(b"\x01\x8e.\t\xa9\x06=\x9b\x0fK\xaa\xdc'\x01\xe0;")
    Id('01HRQ0KA867PDGYJXAVGKG3R1V')
    >>> Id("01HRQ0BNKS4WMFVQPW810MPM3V")
    Id('01HRQ0BNKS4WMFVQPW810MPM3V')
    >>> Id("01HRQ0BNKS4WMFVQPW810MP")
    Traceback (most recent call last):
     ...
    ValueError: Invalid ULID string: 01HRQ0BNKS4WMFVQPW810MP
    """

    def __init__(self, value: Union[str, ULID, bytes]) -> None:
        if isinstance(value, ULID):
            super(Id, self).__init__(value.bytes)
            return
        if isinstance(value, bytes):
            super(Id, self).__init__(value)
            return
        if len(value) != 26:
            raise ValueError(f"Invalid ULID string: {value}")
        super(Id, self).__init__(ulid.base32.decode_ulid(value))

    @classmethod
    def generate(cls: Type[IdT]) -> IdT:
        return cls(ulid.new())

    def serialize(self) -> str:
        """
        Serialize the ULID to a string.

        >>> Id("01HRQ0BNKS4WMFVQPW810MPM3V").serialize()
        '01HRQ0BNKS4WMFVQPW810MPM3V'
        """
        return str(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.str}')"

    @classmethod
    def validate(cls: Type[IdT], value: Any) -> IdT:
        if isinstance(value, cls):
            return value
        if isinstance(value, (ULID, str)):
            return cls(value)
        raise ValueError(f"Cannot convert {value} to {cls}")

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.plain_serializer_function_ser_schema(cls.serialize, when_used="json"),
        )

    def __get_pydantic_json_schema__(self, _handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"format": "crockfordBase32", "type": "string"}


class Timestamp(int):
    """
    Timestamp class
    >>> a = Timestamp(1674397764479000)
    >>> a
    Timestamp(1674397764479000)
    >>> a.milliseconds
    1674397764479
    >>> a.microseconds
    1674397764479000
    >>> a.datetime
    datetime.datetime(2023, 1, 22, 14, 29, 24, 479000, tzinfo=datetime.timezone.utc)
    >>> dt = a.datetime
    >>> ts = dt.timestamp()
    >>> Timestamp(dt)
    Timestamp(1674397764479000)
    >>> Timestamp(ts)
    Timestamp(1674397764479000)
    >>> Timestamp("2023-01-22T14:29:24.422Z")
    Timestamp(1674397764422000)
    >>> Timestamp("2023/02/12 12:21:12")
    Timestamp(1676172072000000)
    >>> Timestamp("invalid")
    Traceback (most recent call last):
      ...
    dateutil.parser._parser.ParserError: Unknown string format: invalid
    >>> from pydantic import TypeAdapter
    >>> ta = TypeAdapter(Timestamp)
    >>> ta.validate_python(1674397764479000)
    Timestamp(1674397764479000)
    >>> ta.validate_python("2023-01-22T14:29:24.422Z")
    Timestamp(1674397764422000)
    >>> ta.validate_python("2023/02/12 12:21:12")
    Timestamp(1676172072000000)
    >>> ta.validate_python("invalid")
    Traceback (most recent call last):
     ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for function-plain[validate()]
      Value error, Unknown string format: invalid [type=value_error, input_value='invalid', input_type=str]
     ...
    """

    def __new__(cls, value: Union[int, float, _datetime, str]) -> "Timestamp":
        if isinstance(value, _datetime):
            return super(Timestamp, cls).__new__(cls, int(value.timestamp() * 1000000))
        if isinstance(value, str):
            return super(Timestamp, cls).__new__(cls, int(parse_datetime(value).timestamp() * 1000000))
        if isinstance(value, float):
            return super(Timestamp, cls).__new__(cls, int(value * 1000000))
        return super(Timestamp, cls).__new__(cls, value)

    @classmethod
    def validate(cls, v: Any) -> "Timestamp":
        if isinstance(v, cls):
            return v
        if isinstance(v, (int, float, _datetime, str)):
            return cls(v)
        raise ValueError(f"Cannot convert {v} to {cls}")

    @property
    def milliseconds(self) -> int:
        """
        >>> a = Timestamp(1674365364479000)
        >>> a.milliseconds
        1674365364479
        """
        return int(self // 1000)

    @property
    def microseconds(self) -> int:
        """
        >>> a = Timestamp(1674365364479000)
        >>> a.microseconds
        1674365364479000
        """
        return int(self)

    @property
    def datetime(self) -> _datetime:
        """
        >>> a = Timestamp(1674397764479000)
        >>> a.datetime
        datetime.datetime(2023, 1, 22, 14, 29, 24, 479000, tzinfo=datetime.timezone.utc)
        """
        return _datetime.fromtimestamp(self / 1000000, tz=_timezone.utc)

    @classmethod
    def now(cls) -> "Timestamp":
        return cls(_datetime.utcnow())

    def __repr__(self) -> str:
        return f"Timestamp({super(Timestamp, self).__repr__()})"

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.plain_serializer_function_ser_schema(cls.serialize, when_used="json"),
        )

    def __get_pydantic_json_schema__(self, _handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"format": "timestamp", "type": "integer"}

    def serialize(self) -> int:
        """
        >>> Timestamp(1674397764479000).serialize()
        1674397764479000
        """
        return int(self)


class BaseModel(PydanticBaseModel):
    """
    >>> from unittest.mock import patch
    >>> from datetime import timedelta, timezone, datetime
    >>> from pydantic import Field
    >>> class DerivedModel(BaseModel):
    ...   object_name: str
    >>> x = DerivedModel(object_name='test')
    >>> x
    DerivedModel(object_name='test')
    >>> x.model_dump()
    {'object_name': 'test'}
    >>> x.model_dump_json()
    '{"objectName":"test"}'
    >>> DerivedModel.model_validate_json('{"objectName":"test2"}')
    DerivedModel(object_name='test2')
    >>> DerivedModel.model_validate_json('{"object_name":"test3"}')
    DerivedModel(object_name='test3')
    >>> DerivedModel.model_json_schema()
    {'properties': {'objectName': {'title': 'Objectname', 'type': 'string'}}, 'required': ['objectName'], 'title': 'DerivedModel', 'type': 'object'}
    """  # noqa: E501

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel, validate_assignment=True)

    def model_dump_json(
        self,
        *,
        indent: int | None = None,
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> str:
        return super(BaseModel, self).model_dump_json(
            indent=indent,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )


class BaseEntity(BaseModel, Generic[IdT]):
    """
    >>> class DerivedId(Id):
    ...   pass
    >>> class DerivedEntity(BaseEntity[DerivedId]):
    ...   ...
    >>> x = DerivedEntity()
    >>> x.id
    DerivedId('...')
    >>> isinstance(x.id, DerivedId)
    True
    >>> DerivedEntity.model_json_schema()
    {'properties': {'id': {'format': 'crockfordBase32', 'title': 'Id', 'type': 'string'}}, 'title': 'DerivedEntity', 'type': 'object'}
    """  # noqa: E501

    id: IdT = Field(default_factory=lambda: cast(IdT, Id.generate()), validate_default=True, frozen=True)


class BaseCreationTimeAwareModel(BaseModel):
    """
    >>> class DerivedCreationTimeAwareModel(BaseCreationTimeAwareModel):
    ...   ...
    >>> x = DerivedCreationTimeAwareModel()
    >>> x.created_at
    Timestamp(...)
    >>> DerivedCreationTimeAwareModel.model_json_schema()
    {'properties': {'createdAt': {'format': 'timestamp', 'title': 'Createdat', 'type': 'integer'}}, 'title': 'DerivedCreationTimeAwareModel', 'type': 'object'}
    """  # noqa: E501

    created_at: Timestamp = Field(default_factory=Timestamp.now, validate_default=True, frozen=True)


class BaseUpdateTimeAwareModel(BaseCreationTimeAwareModel):
    """
    >>> class DerivedUpdateTimeAwareModel(BaseUpdateTimeAwareModel):
    ...     ...
    >>> x = DerivedUpdateTimeAwareModel()
    >>> x.updated_at
    Timestamp(...)
    >>> x.created_at
    Timestamp(...)
    >>> DerivedUpdateTimeAwareModel.model_json_schema()
    {'properties': {'createdAt': {'format': 'timestamp', 'title': 'Createdat', 'type': 'integer'}, 'updatedAt': {'format': 'timestamp', 'title': 'Updatedat', 'type': 'integer'}}, 'title': 'DerivedUpdateTimeAwareModel', 'type': 'object'}
    """  # noqa: E501

    updated_at: Timestamp = Field(default_factory=Timestamp.now, validate_default=True)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "updated_at":
            return super(BaseUpdateTimeAwareModel, self).__setattr__(name, value)
        try:
            super(BaseUpdateTimeAwareModel, self).__setattr__(name, value)
        except Exception as e:
            raise e
        super(BaseUpdateTimeAwareModel, self).__setattr__("updated_at", Timestamp.now())
