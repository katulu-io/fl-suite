# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: spire/api/types/jointoken.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fspire/api/types/jointoken.proto\x12\x0fspire.api.types\".\n\tJoinToken\x12\r\n\x05value\x18\x01 \x01(\t\x12\x12\n\nexpires_at\x18\x02 \x01(\x03\x42\x37Z5github.com/spiffe/spire-api-sdk/proto/spire/api/typesb\x06proto3')



_JOINTOKEN = DESCRIPTOR.message_types_by_name['JoinToken']
JoinToken = _reflection.GeneratedProtocolMessageType('JoinToken', (_message.Message,), {
  'DESCRIPTOR' : _JOINTOKEN,
  '__module__' : 'spire.api.types.jointoken_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.types.JoinToken)
  })
_sym_db.RegisterMessage(JoinToken)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z5github.com/spiffe/spire-api-sdk/proto/spire/api/types'
  _JOINTOKEN._serialized_start=52
  _JOINTOKEN._serialized_end=98
# @@protoc_insertion_point(module_scope)