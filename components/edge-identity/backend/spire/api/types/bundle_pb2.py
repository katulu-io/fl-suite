# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: spire/api/types/bundle.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1cspire/api/types/bundle.proto\x12\x0fspire.api.types\"\xbb\x01\n\x06\x42undle\x12\x14\n\x0ctrust_domain\x18\x01 \x01(\t\x12:\n\x10x509_authorities\x18\x02 \x03(\x0b\x32 .spire.api.types.X509Certificate\x12\x30\n\x0fjwt_authorities\x18\x03 \x03(\x0b\x32\x17.spire.api.types.JWTKey\x12\x14\n\x0crefresh_hint\x18\x04 \x01(\x03\x12\x17\n\x0fsequence_number\x18\x05 \x01(\x04\"\x1f\n\x0fX509Certificate\x12\x0c\n\x04\x61sn1\x18\x01 \x01(\x0c\"@\n\x06JWTKey\x12\x12\n\npublic_key\x18\x01 \x01(\x0c\x12\x0e\n\x06key_id\x18\x02 \x01(\t\x12\x12\n\nexpires_at\x18\x03 \x01(\x03\"n\n\nBundleMask\x12\x18\n\x10x509_authorities\x18\x02 \x01(\x08\x12\x17\n\x0fjwt_authorities\x18\x03 \x01(\x08\x12\x14\n\x0crefresh_hint\x18\x04 \x01(\x08\x12\x17\n\x0fsequence_number\x18\x05 \x01(\x08\x42\x37Z5github.com/spiffe/spire-api-sdk/proto/spire/api/typesb\x06proto3')



_BUNDLE = DESCRIPTOR.message_types_by_name['Bundle']
_X509CERTIFICATE = DESCRIPTOR.message_types_by_name['X509Certificate']
_JWTKEY = DESCRIPTOR.message_types_by_name['JWTKey']
_BUNDLEMASK = DESCRIPTOR.message_types_by_name['BundleMask']
Bundle = _reflection.GeneratedProtocolMessageType('Bundle', (_message.Message,), {
  'DESCRIPTOR' : _BUNDLE,
  '__module__' : 'spire.api.types.bundle_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.types.Bundle)
  })
_sym_db.RegisterMessage(Bundle)

X509Certificate = _reflection.GeneratedProtocolMessageType('X509Certificate', (_message.Message,), {
  'DESCRIPTOR' : _X509CERTIFICATE,
  '__module__' : 'spire.api.types.bundle_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.types.X509Certificate)
  })
_sym_db.RegisterMessage(X509Certificate)

JWTKey = _reflection.GeneratedProtocolMessageType('JWTKey', (_message.Message,), {
  'DESCRIPTOR' : _JWTKEY,
  '__module__' : 'spire.api.types.bundle_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.types.JWTKey)
  })
_sym_db.RegisterMessage(JWTKey)

BundleMask = _reflection.GeneratedProtocolMessageType('BundleMask', (_message.Message,), {
  'DESCRIPTOR' : _BUNDLEMASK,
  '__module__' : 'spire.api.types.bundle_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.types.BundleMask)
  })
_sym_db.RegisterMessage(BundleMask)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z5github.com/spiffe/spire-api-sdk/proto/spire/api/types'
  _BUNDLE._serialized_start=50
  _BUNDLE._serialized_end=237
  _X509CERTIFICATE._serialized_start=239
  _X509CERTIFICATE._serialized_end=270
  _JWTKEY._serialized_start=272
  _JWTKEY._serialized_end=336
  _BUNDLEMASK._serialized_start=338
  _BUNDLEMASK._serialized_end=448
# @@protoc_insertion_point(module_scope)