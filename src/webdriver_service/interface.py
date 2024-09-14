
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, fields, MISSING
from enum import Enum, EnumMeta
from typing import Dict, List, Optional, Type, TypeVar, Generic, get_args, get_type_hints, MutableMapping, cast
from google.protobuf.message import Message
from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper

from .build import interface_pb2 as pb2


T = TypeVar('T', bound=Message)
E = TypeVar('E')

class ABCEnum(ABCMeta, EnumMeta):
    def __new__(mcls, *args, **kw):
        abstract_enum_cls = super().__new__(mcls, *args, **kw)
        # Only check abstractions if members were defined.
        if abstract_enum_cls._member_map_:
            try:  # Handle existence of undefined abstract methods.
                absmethods = list(abstract_enum_cls.__abstractmethods__)
                if absmethods:
                    missing = ', '.join(f'{method!r}' for method in absmethods)
                    plural = 's' if len(absmethods) > 1 else ''
                    raise TypeError(
                       f"cannot instantiate abstract class {abstract_enum_cls.__name__!r}"
                       f" with abstract method{plural} {missing}")
            except AttributeError:
                pass
        return abstract_enum_cls
	
class BaseEnum(Enum, metaclass=ABCEnum):
	@abstractmethod
	def get_proto_enum(self): ...



@dataclass
class BaseData(Generic[T]):

	def to_message(self) -> T:
		"""
		Dataclass to Protobuf Message
		"""
		message_class:Type[T] = self._get_T()
		
		kw = {}
		for f in fields(self):
			val = getattr(self,f.name)
			if f.type == "Optional[str]" and val is None:
				val = ""
			elif issubclass(type(val),BaseEnum):
				v = cast(BaseEnum,val)
				e = v.get_proto_enum()
				val = getattr(e,v.name)
			elif issubclass(type(val),BaseData):
				val = val.to_message()
			kw[f.name] = val
		message = message_class(**kw)
		self._check_fields_consistency(message)
		return message
	
	@classmethod
	def from_message(cls, message:T):
		"""
		Factory method to init a Dataclass from its corresponding Message
		"""
		if cls._get_T() != type(message):
			raise TypeError(f"Proto Message type mismatch. Expected {type(T)}")
		cls._check_for_required(message)
		cls._check_fields_consistency(message)
		kwargs = cls._get_message_values(message)
		return cls(**kwargs)

	@staticmethod
	def _are_same(l1: List[str], l2:List[str]):
		ln1 = len(l1)
		if ln1 != len(l2):
			return False
		l1.sort()
		l2.sort()
		for i in range(ln1):
			if l1[i] != l2[i]:
				return False
		return True
	
	@classmethod
	# XXX: This is a hack!!! I need to change this later
	def _get_T(cls, pos=0) -> Type[T]:
		"""
		Gets the class of Generic type (T).
		It works by getting the originating base class at position 'pos'
		the pos is by default 0, you don't need to change it but
		always check it.
		"""
		return get_args(cls.__orig_bases__[pos])[0] # type: ignore

	@classmethod
	def _check_fields_consistency(cls,m:Message):
		"""
		Checks to see if fields in both Dataclass and Message are the same
		"""
		cls_fields = [f.name for f in fields(cls)]
		ms_fields = [field.name for field in m.DESCRIPTOR.fields]
		if not cls._are_same(cls_fields,ms_fields):
			raise ValueError(f"Field inconsistency. Dataclass: '{cls.__qualname__}'"\
					f" proto message: '{type(m).__name__}'")
		
	@classmethod
	def _check_for_required(cls, m:Message):
		"""
		Checks whether required fields are set in the given Message
		"""
		ms_fields = [f.name for f, _ in m.ListFields()]
		missing_required = []
		for f in fields(cls):
			# Missing default value means it's required
			if (f.default == MISSING and f.default_factory == MISSING) and f.name not in ms_fields:
				missing_required.append(f.name)
		if len(missing_required) > 0:
			raise ValueError(f"Missing required fields: {'-'.join(missing_required)}")
	
	@classmethod
	def _get_field_type(cls,f_name:str):
		type_hint = get_type_hints(cls)[f_name]
		type_args = get_args(type_hint)
		if len(type_args) > 0:
			return type_args[0]
		return type_hint
	
	@classmethod
	def _get_message_values(cls, m:Message):
		"""
		Gets each field value from the message and returns 
		a dict of kwargs {field name:value}
		If the field is unset (it's not shown in ListFields()) the default value from
		Message is NOT taken and the default value is left to the corresponding Dataclass
		It converts empty strings to None
		"""
		kwargs = {}
		for descriptor, value in m.ListFields():
			if descriptor.type == descriptor.TYPE_ENUM:
				# Convert proto enum to python Enum
				enum_class: Type[BaseEnum] = cls._get_field_type(descriptor.name)
				value = enum_class(value=value)
			elif issubclass(type(value),Message):
				# The message contains another message which in turn should be
				# mapped to another dataclass
				d_class:Type[BaseData] = cls._get_field_type(descriptor.name)
				value = d_class.from_message(value)
			elif descriptor.type == descriptor.TYPE_STRING and value == "":
				value = None
			elif issubclass(type(value),MutableMapping):
				value = dict(value)
			kwargs[descriptor.name] = value
		return kwargs


class StatusType(BaseEnum):
	STATUS_OK = 0
	STATUS_FAILURE = 1

	def get_proto_enum(self):
		return pb2.StatusType

@dataclass
class DriverOptions(BaseData[pb2.DriverOptions]):
	headless: bool = False
	load_timeout: int = 12
	disable_extension: bool = False
	debug_address: Optional[str] = None
	driver_logging: bool = False
	user_data_dir: Optional[str] = None

@dataclass
class Credentials(BaseData[pb2.Credentials]):
	username:str
	password: str

@dataclass
class Payload(BaseData[pb2.Payload]):
	images: Optional[Dict[str,bytes]] = None

@dataclass
class ServiceResponse(BaseData[pb2.ServiceResponse]):
	status: StatusType = StatusType.STATUS_OK
	message: Optional[str] = None
	exception: Optional[str] = None
	payload: Optional[Payload] = None

@dataclass
class WebdriverRequest(BaseData[pb2.WebdriverRequest]):
	url: Optional[str] = None

@dataclass
class Empty(BaseData[pb2.Empty]): ...


