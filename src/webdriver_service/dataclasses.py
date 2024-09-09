
from __future__ import annotations

from dataclasses import dataclass, fields
from typing import List, Optional, TypeVar, Generic, get_args, Type
from google.protobuf.message import Message

from .build import interface_pb2 as pb2

T = TypeVar('T', bound=Message)

@dataclass
class BaseData(Generic[T]):

	def to_message(self) -> T: # type: ignore

		# XXX: This is a hack!!! I need to change this later
		# This gets the class of T and instantiate it.
		message = get_args(self.__orig_bases__[0])[0]() # type: ignore
		self.check_message_fields_consistency(message)
		for f in fields(self):
			val = getattr(self,f.name)
			if f.type == "Optional[str]" and val is None:
				val = ""
			setattr(message,f.name,val)
		return message
	
	@classmethod
	def from_message(cls, message:T):
		if type(T) != type(message):
			print("shite")
		c = cls()
		cls.check_message_fields_consistency(message)
		for descriptor, value in message.ListFields():
			if descriptor.type == str and value == "":
				value = None
			setattr(c,descriptor.name,value)
		return c

	@staticmethod
	def are_same(l1: List[str], l2:List[str]):
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
	def check_message_fields_consistency(cls,m:Message):
		cls_fields = [f.name for f in fields(cls)]
		ms_fields = [field.name for field in m.DESCRIPTOR.fields]
		if not cls.are_same(cls_fields,ms_fields):
			raise ValueError(f"Inconsistency between the dataclass '{cls.__qualname__}'"\
					f" and proto message '{type(m).__name__}'")

@dataclass
class DriverOptions(BaseData[pb2.DriverOptions]):
	headless: bool = False
	load_timeout: int = 12
	disable_extension: bool = False
	debug_address: Optional[str] = None
	driver_logging: bool = False
	user_data_dir: Optional[str] = None