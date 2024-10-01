import re
from base64 import standard_b64decode, standard_b64encode
from datetime import datetime as _datetime
from datetime import timezone as _timezone
from typing import Any, Dict, Generic, Literal, Sequence, Type, TypeVar, Union, cast

import ulid
from dateutil.parser import parse as parse_datetime
from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    ConfigDict,
    DirectoryPath,
    Field,
    FilePath,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    NewPath,
    TypeAdapter,
    create_model,
)
from pydantic.alias_generators import to_camel, to_snake
from pydantic.json_schema import JsonSchemaValue
from pydantic.main import IncEx
from pydantic_core import core_schema
from ulid import ULID

from .utils import normalize_jptext

StringT = TypeVar("StringT", bound="BaseString")
BytesT = TypeVar("BytesT", bound="BaseBytes")
IntegerT = TypeVar("IntegerT", bound="BaseInteger")
FloatT = TypeVar("FloatT", bound="BaseFloat")
IdT = TypeVar("IdT", bound="Id")
JsonAcceptable = Union[str, int, float, bool, None, dict[str, "JsonAcceptable"], list["JsonAcceptable"]]
NewOrExistingFilePath = Union[FilePath, NewPath]
NewOrExistingDirectoryPath = Union[DirectoryPath, NewPath]


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

    def serialize(self) -> JsonAcceptable:
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

    def serialize(self) -> JsonAcceptable:
        return str(self)

    @classmethod
    def __get_extra_constraint_dict__(cls) -> dict[str, Any]:
        return {}

    def __hash__(self) -> int:
        return super(BaseString, self).__hash__()

    @classmethod
    def from_str(cls: Type[StringT], v: str) -> StringT:
        return TypeAdapter(cls).validate_python(v)


class LimitedMinLengthStringMixIn(BaseString):
    """
    LimitedMinLengthStringMixIn is a string type that can be used to validate and serialize strings with a minimum length.

    >>> class TestString(LimitedMinLengthStringMixIn, BaseString):
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


class NonEmptyStringMixIn(LimitedMinLengthStringMixIn, metaclass=type):
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


class LimitedMaxLengthStringMixIn(BaseString):
    """
    LimitedMaxLengthStringMixIn is a string type that can be used to validate and serialize strings with a maximum length.

    >>> class TestString(LimitedMaxLengthStringMixIn, BaseString):
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
    >>> class MultipleSubstitutionTestString(RegexSubstitutedStringMixIn, BaseString):
    ...   @classmethod
    ...   def get_pattern_to_repl_map(cls) -> Dict[str, str]:
    ...     return {"[\n\r]": " ", r"([a-z]*)": r"\1\1"}
    >>> MultipleSubstitutionTestString.from_str("test\ntest")
    MultipleSubstitutionTestString('testtest testtest')
    """

    @classmethod
    def get_pattern(cls) -> str:
        raise NotImplementedError

    @classmethod
    def get_repl(cls) -> str:
        raise NotImplementedError

    @classmethod
    def get_pattern_to_repl_map(cls) -> Dict[str, str]:
        return {cls.get_pattern(): cls.get_repl()}

    @classmethod
    def _proc_str(cls, s: str) -> str:
        for pattern, repl in cls.get_pattern_to_repl_map().items():
            s = re.sub(pattern, repl, s)
        return super()._proc_str(s)


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
    >>> ta.validate_python("alreadyCamelCasedWontBeLowerCased")
    TestString('alreadyCamelCasedWontBeLowerCased')
    """

    @classmethod
    def _proc_str(cls, s: str) -> str:
        return super()._proc_str(to_camel(s))


class BaseInteger(int):
    """
    BaseInteger is an integer type that can be used to validate and serialize integers.

    >>> BaseInteger(123)
    BaseInteger(123)
    >>> int(BaseInteger(123))
    123
    >>> ta = TypeAdapter(BaseInteger)
    >>> ta.validate_python(123)
    BaseInteger(123)
    >>> ta.validate_python("string")
    Traceback (most recent call last):
     ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for function-after[validate(), int]
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='string', input_type=str]
     ...
    >>> ta.dump_json(BaseInteger(123))
    b'123'
    >>> hash(BaseInteger(123)) == hash(123)
    True
    """  # noqa: E501

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __str__(self) -> str:
        return super(BaseInteger, self).__str__()

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.int_schema(**cls.__get_extra_constraint_dict__()),
            serialization=core_schema.plain_serializer_function_ser_schema(cls.serialize, when_used="json"),
        )

    def __get_pydantic_json_schema__(self, _handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"type": "integer"}

    @classmethod
    def validate(cls: Type[IntegerT], value: Any) -> IntegerT:
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            return cls(value)
        raise ValueError(f"Cannot convert {value} to {cls.__name__}")

    def serialize(self) -> JsonAcceptable:
        return int(self)

    @classmethod
    def __get_extra_constraint_dict__(cls) -> dict[str, Any]:
        return {}

    def __hash__(self) -> int:
        return super(BaseInteger, self).__hash__()


class LowerBoundIntegerMixIn(BaseInteger):
    """
    LowerBoundIntegerMixIn is an integer type that can be used to validate and serialize integers with a lower bound.

    >>> class TestInteger(LowerBoundIntegerMixIn):
    ...   LowerBoundIntegerMixIn, BaseInteger
    ...   @classmethod
    ...   def get_min_value(cls) -> int:
    ...     return 3
    >>> TestInteger(3)
    TestInteger(3)
    >>> ta = TypeAdapter(TestInteger)
    >>> ta.validate_python(3)
    TestInteger(3)
    >>> ta.validate_python(2)
    Traceback (most recent call last):
     ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for function-after[validate(), constrained-int]
      Input should be greater than or equal to 3 [type=greater_than_equal, input_value=2, input_type=int]
     ...
    """  # noqa: E501

    @classmethod
    def get_min_value(cls) -> int:
        raise NotImplementedError

    @classmethod
    def __get_extra_constraint_dict__(cls) -> dict[str, Any]:
        return super().__get_extra_constraint_dict__() | {"ge": cls.get_min_value()}


class BaseFloat(float):
    """
    BaseFloat is a float type that can be used to validate and serialize floats.

    >>> BaseFloat(123.0)
    BaseFloat(123.0)
    >>> float(BaseFloat(123.0))
    123.0
    >>> ta = TypeAdapter(BaseFloat)
    >>> ta.validate_python(123.0)
    BaseFloat(123.0)
    >>> ta.validate_python("string")
    Traceback (most recent call last):
     ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for function-after[validate(), float]
      Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='string', input_type=str]
     ...
    >>> ta.dump_json(BaseFloat(123.0))
    b'123.0'
    >>> hash(BaseFloat(123.0)) == hash(123.0)
    True
    """  # noqa: E501

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    def __str__(self) -> str:
        return super(BaseFloat, self).__str__()

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.float_schema(**cls.__get_extra_constraint_dict__()),
            serialization=core_schema.plain_serializer_function_ser_schema(cls.serialize, when_used="json"),
        )

    def __get_pydantic_json_schema__(self, _handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"type": "number"}

    @classmethod
    def validate(cls: Type[FloatT], value: Any) -> FloatT:
        if isinstance(value, cls):
            return value
        if isinstance(value, float):
            return cls(value)
        raise ValueError(f"Cannot convert {value} to {cls.__name__}")

    def serialize(self) -> JsonAcceptable:
        return float(self)

    @classmethod
    def __get_extra_constraint_dict__(cls) -> dict[str, Any]:
        return {}

    def __hash__(self) -> int:
        return super(BaseFloat, self).__hash__()


class LowerBoundFloatMixIn(BaseFloat):
    """
    LowerBoundFloatMixIn is a float type that can be used to validate and serialize floats with a lower bound.

    >>> class TestFloat(LowerBoundFloatMixIn):
    ...   LowerBoundFloatMixIn, BaseFloat
    ...   @classmethod
    ...   def get_min_value(cls) -> float:
    ...     return 3.0
    >>> TestFloat(3.0)
    TestFloat(3.0)
    >>> ta = TypeAdapter(TestFloat)
    >>> ta.validate_python(3.0)
    TestFloat(3.0)
    >>> ta.validate_python(2.9)
    Traceback (most recent call last):
     ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for function-after[validate(), constrained-float]
      Input should be greater than or equal to 3 [type=greater_than_equal, input_value=2.9, input_type=float]
     ...
    """  # noqa: E501

    @classmethod
    def get_min_value(cls) -> float:
        raise NotImplementedError

    @classmethod
    def __get_extra_constraint_dict__(cls) -> dict[str, Any]:
        return super().__get_extra_constraint_dict__() | {"ge": cls.get_min_value()}


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
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: JsonSchemaValue | None = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none"] | Literal["warn"] | Literal["error"] = True,
        serialize_as_any: bool = False,
    ) -> str:
        return super().model_dump_json(
            indent=indent,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any,
        )


def _json_schema_type_to_python_type(json_schema_type: Dict[str, Any], defs: Dict[str, Type[BaseModel]]) -> Type[Any]:
    primitive_map: Dict[str, Type[int | str | float | bool]] = {
        "integer": int,
        "string": str,
        "number": float,
        "boolean": bool,
    }
    if "type" in json_schema_type:
        t = json_schema_type["type"]
        if t in primitive_map:
            return primitive_map[t]
        if t == "array":
            if "items" in json_schema_type:
                items = json_schema_type["items"]
                if "type" in items:
                    tt = primitive_map[items["type"]]
                    if isinstance(tt, type):
                        return Sequence[tt]  # type: ignore[valid-type]
                    raise ValueError(f"Cannot convert {json_schema_type} to Python type")
                if "$ref" in items:
                    reftype = items["$ref"]
                    if reftype in defs:
                        return Sequence[defs[reftype]]  # type: ignore[valid-type]
                    raise ValueError(f"Cannot convert {json_schema_type} to Python type")
            return list
        if t == "object":
            if "$ref" in json_schema_type:
                return defs[json_schema_type["$ref"]]
            return dict
    if "$ref" in json_schema_type:
        return defs[json_schema_type["$ref"]]
    raise ValueError(f"Cannot convert {json_schema_type} to Python type")


def _property_to_model(
    json_schema: Dict[str, Any], defs: Dict[str, Any], base_model: Type[BaseModel] = BaseModel
) -> Type[BaseModel]:
    """
    >>> x = {'properties': {'value': {'title': 'Value', 'type': 'string'}}, 'required': ['value'], 'title': 'UrlModel', 'type': 'object'}
    >>> x_model = _property_to_model(x, {})
    >>> x_model(value="http://localhost")
    UrlModel(value='http://localhost')
    >>> y = {'properties': {'url': {'$ref': '#/$defs/UrlModel'}}, 'required': ['url'], 'title': 'MyModel', 'type': 'object'}
    >>> _property_to_model(y, {'#/$defs/UrlModel': x_model})(url={"value": "http://localhost"})
    MyModel(url=UrlModel(value='http://localhost'))
    """  # noqa: E501
    class_name = (
        json_schema["title"] if "title" in json_schema and isinstance(json_schema["title"], str) else "GeneratedModel"
    )
    dynamic_model = create_model(
        class_name,
        __base__=base_model,
        **{to_snake(k): (_json_schema_type_to_python_type(v, defs), ...) for k, v in json_schema["properties"].items()},
    )  # type: ignore[call-overload]
    if not isinstance(dynamic_model, type):
        raise ValueError("create_model failed")
    return dynamic_model


def json_schema_to_model(json_schema: Dict[str, Any], base_model: Type[BaseModel] = BaseModel) -> Type[BaseModel]:
    """
    >>> x = {
    ...   '$defs': {
    ...     'MyNestedModel': {
    ...       'properties': {'obj': {'$ref': '#/$defs/MyNestedNestedModel'}},
    ...       'required': ['obj'],
    ...       'title': 'MyNestedModel',
    ...       'type': 'object'
    ...     },
    ...     'MyNestedNestedModel': {
    ...       'properties': {'name': {'title': 'Name', 'type': 'string'}, 'age': {'title': 'Age', 'type': 'integer'}},
    ...       'required': ['name', 'age'],
    ...       'title': 'MyNestedNestedModel',
    ...       'type': 'object'
    ...     }
    ...   },
    ...   'properties': {'nested': {'$ref': '#/$defs/MyNestedModel'}},
    ...   'required': ['nested'],
    ...   'title': 'MyModel',
    ...   'type': 'object'
    ... }
    >>> generated_model = json_schema_to_model(x)
    >>> generated_model(nested={"obj": {"name": "foo", "age": 42}, "flag": True})
    MyModel(nested=MyNestedModel(obj=MyNestedNestedModel(name='foo', age=42)))
    """
    if "properties" not in json_schema:
        raise ValueError("properties key is not found in json_schema")
    unresolved_refs = json_schema.get("$defs", {})
    resolved_refs: Dict[str, Type[BaseModel]] = {}
    while unresolved_refs:
        before_len = len(unresolved_refs)
        key_seq = list(unresolved_refs.keys())
        for k in key_seq:
            try:
                resolved_refs[f"#/$defs/{k}"] = _property_to_model(
                    unresolved_refs[k], resolved_refs, base_model=base_model
                )
                unresolved_refs.pop(k)
            except KeyError:
                continue
            ...
        if before_len == len(unresolved_refs):
            raise ValueError("Cannot resolve all references")

    return _property_to_model(json_schema, resolved_refs, base_model=base_model)


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
