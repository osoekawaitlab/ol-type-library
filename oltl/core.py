from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar, Union

import ulid
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, TypeAdapter
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from ulid import ULID

StrT = TypeVar("StrT", bound="BaseString")
IdT = TypeVar("IdT", bound="Id")


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
    pydantic_core._pydantic_core.ValidationError: 1 validation error for function-after[validate(), str]
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
    """

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
            cls.validate,
            core_schema.str_schema(**cls.__get_extra_constraint_dict__()),
            serialization=core_schema.plain_serializer_function_ser_schema(cls.serialize, when_used="json"),
        )

    @classmethod
    def validate(cls: Type[StrT], v: Any) -> StrT:
        return cls(cls._proc_str(v))

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


class LimitedMinLengthMixin(ABC, BaseString):
    @classmethod
    @abstractmethod
    def get_min_length(cls) -> int:
        raise NotImplementedError

    @classmethod
    def __get_extra_constraint_dict__(cls) -> dict[str, Any]:
        return super().__get_extra_constraint_dict__() | {"min_length": cls.get_min_length()}


class NonEmptyString(LimitedMinLengthMixin, BaseString):
    """
    NonEmptyString is a string type that can be used to validate and serialize non-empty strings.

    >>> NonEmptyString.from_str("test")
    NonEmptyString('test')
    >>> ta = TypeAdapter(NonEmptyString)
    >>> ta.validate_python("test")
    NonEmptyString('test')
    >>> ta.validate_python("")
    Traceback (most recent call last):
     ...
    pydantic_core._pydantic_core.ValidationError: 1 validation error for function-after[validate(), constrained-str]
      String should have at least 1 character [type=string_too_short, input_value='', input_type=str]
     ...
    """

    @classmethod
    def get_min_length(cls) -> int:
        return 1


class LimitedMaxLengthMixin(ABC, BaseString):
    @classmethod
    @abstractmethod
    def get_max_length(cls) -> int:
        raise NotImplementedError

    @classmethod
    def __get_extra_constraint_dict__(cls) -> dict[str, Any]:
        return super().__get_extra_constraint_dict__() | {"max_length": cls.get_max_length()}


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
