# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: spire/api/server/entry/v1/entry.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from spire.api.types import entry_pb2 as spire_dot_api_dot_types_dot_entry__pb2
from spire.api.types import federateswith_pb2 as spire_dot_api_dot_types_dot_federateswith__pb2
from spire.api.types import selector_pb2 as spire_dot_api_dot_types_dot_selector__pb2
from spire.api.types import spiffeid_pb2 as spire_dot_api_dot_types_dot_spiffeid__pb2
from spire.api.types import status_pb2 as spire_dot_api_dot_types_dot_status__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n%spire/api/server/entry/v1/entry.proto\x12\x19spire.api.server.entry.v1\x1a\x1bspire/api/types/entry.proto\x1a#spire/api/types/federateswith.proto\x1a\x1espire/api/types/selector.proto\x1a\x1espire/api/types/spiffeid.proto\x1a\x1cspire/api/types/status.proto\"\x15\n\x13\x43ountEntriesRequest\"%\n\x14\x43ountEntriesResponse\x12\r\n\x05\x63ount\x18\x01 \x01(\x05\"\x95\x03\n\x12ListEntriesRequest\x12\x44\n\x06\x66ilter\x18\x01 \x01(\x0b\x32\x34.spire.api.server.entry.v1.ListEntriesRequest.Filter\x12/\n\x0boutput_mask\x18\x02 \x01(\x0b\x32\x1a.spire.api.types.EntryMask\x12\x11\n\tpage_size\x18\x03 \x01(\x05\x12\x12\n\npage_token\x18\x04 \x01(\t\x1a\xe0\x01\n\x06\x46ilter\x12/\n\x0c\x62y_spiffe_id\x18\x01 \x01(\x0b\x32\x19.spire.api.types.SPIFFEID\x12/\n\x0c\x62y_parent_id\x18\x02 \x01(\x0b\x32\x19.spire.api.types.SPIFFEID\x12\x34\n\x0c\x62y_selectors\x18\x03 \x01(\x0b\x32\x1e.spire.api.types.SelectorMatch\x12>\n\x11\x62y_federates_with\x18\x04 \x01(\x0b\x32#.spire.api.types.FederatesWithMatch\"W\n\x13ListEntriesResponse\x12\'\n\x07\x65ntries\x18\x01 \x03(\x0b\x32\x16.spire.api.types.Entry\x12\x17\n\x0fnext_page_token\x18\x02 \x01(\t\"N\n\x0fGetEntryRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12/\n\x0boutput_mask\x18\x02 \x01(\x0b\x32\x1a.spire.api.types.EntryMask\"s\n\x17\x42\x61tchCreateEntryRequest\x12\'\n\x07\x65ntries\x18\x01 \x03(\x0b\x32\x16.spire.api.types.Entry\x12/\n\x0boutput_mask\x18\x02 \x01(\x0b\x32\x1a.spire.api.types.EntryMask\"\xc1\x01\n\x18\x42\x61tchCreateEntryResponse\x12K\n\x07results\x18\x01 \x03(\x0b\x32:.spire.api.server.entry.v1.BatchCreateEntryResponse.Result\x1aX\n\x06Result\x12\'\n\x06status\x18\x01 \x01(\x0b\x32\x17.spire.api.types.Status\x12%\n\x05\x65ntry\x18\x02 \x01(\x0b\x32\x16.spire.api.types.Entry\"\xa3\x01\n\x17\x42\x61tchUpdateEntryRequest\x12\'\n\x07\x65ntries\x18\x01 \x03(\x0b\x32\x16.spire.api.types.Entry\x12.\n\ninput_mask\x18\x02 \x01(\x0b\x32\x1a.spire.api.types.EntryMask\x12/\n\x0boutput_mask\x18\x03 \x01(\x0b\x32\x1a.spire.api.types.EntryMask\"\xc1\x01\n\x18\x42\x61tchUpdateEntryResponse\x12K\n\x07results\x18\x01 \x03(\x0b\x32:.spire.api.server.entry.v1.BatchUpdateEntryResponse.Result\x1aX\n\x06Result\x12\'\n\x06status\x18\x01 \x01(\x0b\x32\x17.spire.api.types.Status\x12%\n\x05\x65ntry\x18\x02 \x01(\x0b\x32\x16.spire.api.types.Entry\"&\n\x17\x42\x61tchDeleteEntryRequest\x12\x0b\n\x03ids\x18\x01 \x03(\t\"\xa6\x01\n\x18\x42\x61tchDeleteEntryResponse\x12K\n\x07results\x18\x01 \x03(\x0b\x32:.spire.api.server.entry.v1.BatchDeleteEntryResponse.Result\x1a=\n\x06Result\x12\'\n\x06status\x18\x01 \x01(\x0b\x32\x17.spire.api.types.Status\x12\n\n\x02id\x18\x02 \x01(\t\"N\n\x1bGetAuthorizedEntriesRequest\x12/\n\x0boutput_mask\x18\x01 \x01(\x0b\x32\x1a.spire.api.types.EntryMask\"G\n\x1cGetAuthorizedEntriesResponse\x12\'\n\x07\x65ntries\x18\x01 \x03(\x0b\x32\x16.spire.api.types.Entry2\xb7\x06\n\x05\x45ntry\x12o\n\x0c\x43ountEntries\x12..spire.api.server.entry.v1.CountEntriesRequest\x1a/.spire.api.server.entry.v1.CountEntriesResponse\x12l\n\x0bListEntries\x12-.spire.api.server.entry.v1.ListEntriesRequest\x1a..spire.api.server.entry.v1.ListEntriesResponse\x12N\n\x08GetEntry\x12*.spire.api.server.entry.v1.GetEntryRequest\x1a\x16.spire.api.types.Entry\x12{\n\x10\x42\x61tchCreateEntry\x12\x32.spire.api.server.entry.v1.BatchCreateEntryRequest\x1a\x33.spire.api.server.entry.v1.BatchCreateEntryResponse\x12{\n\x10\x42\x61tchUpdateEntry\x12\x32.spire.api.server.entry.v1.BatchUpdateEntryRequest\x1a\x33.spire.api.server.entry.v1.BatchUpdateEntryResponse\x12{\n\x10\x42\x61tchDeleteEntry\x12\x32.spire.api.server.entry.v1.BatchDeleteEntryRequest\x1a\x33.spire.api.server.entry.v1.BatchDeleteEntryResponse\x12\x87\x01\n\x14GetAuthorizedEntries\x12\x36.spire.api.server.entry.v1.GetAuthorizedEntriesRequest\x1a\x37.spire.api.server.entry.v1.GetAuthorizedEntriesResponseBIZGgithub.com/spiffe/spire-api-sdk/proto/spire/api/server/entry/v1;entryv1b\x06proto3')



_COUNTENTRIESREQUEST = DESCRIPTOR.message_types_by_name['CountEntriesRequest']
_COUNTENTRIESRESPONSE = DESCRIPTOR.message_types_by_name['CountEntriesResponse']
_LISTENTRIESREQUEST = DESCRIPTOR.message_types_by_name['ListEntriesRequest']
_LISTENTRIESREQUEST_FILTER = _LISTENTRIESREQUEST.nested_types_by_name['Filter']
_LISTENTRIESRESPONSE = DESCRIPTOR.message_types_by_name['ListEntriesResponse']
_GETENTRYREQUEST = DESCRIPTOR.message_types_by_name['GetEntryRequest']
_BATCHCREATEENTRYREQUEST = DESCRIPTOR.message_types_by_name['BatchCreateEntryRequest']
_BATCHCREATEENTRYRESPONSE = DESCRIPTOR.message_types_by_name['BatchCreateEntryResponse']
_BATCHCREATEENTRYRESPONSE_RESULT = _BATCHCREATEENTRYRESPONSE.nested_types_by_name['Result']
_BATCHUPDATEENTRYREQUEST = DESCRIPTOR.message_types_by_name['BatchUpdateEntryRequest']
_BATCHUPDATEENTRYRESPONSE = DESCRIPTOR.message_types_by_name['BatchUpdateEntryResponse']
_BATCHUPDATEENTRYRESPONSE_RESULT = _BATCHUPDATEENTRYRESPONSE.nested_types_by_name['Result']
_BATCHDELETEENTRYREQUEST = DESCRIPTOR.message_types_by_name['BatchDeleteEntryRequest']
_BATCHDELETEENTRYRESPONSE = DESCRIPTOR.message_types_by_name['BatchDeleteEntryResponse']
_BATCHDELETEENTRYRESPONSE_RESULT = _BATCHDELETEENTRYRESPONSE.nested_types_by_name['Result']
_GETAUTHORIZEDENTRIESREQUEST = DESCRIPTOR.message_types_by_name['GetAuthorizedEntriesRequest']
_GETAUTHORIZEDENTRIESRESPONSE = DESCRIPTOR.message_types_by_name['GetAuthorizedEntriesResponse']
CountEntriesRequest = _reflection.GeneratedProtocolMessageType('CountEntriesRequest', (_message.Message,), {
  'DESCRIPTOR' : _COUNTENTRIESREQUEST,
  '__module__' : 'spire.api.server.entry.v1.entry_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.CountEntriesRequest)
  })
_sym_db.RegisterMessage(CountEntriesRequest)

CountEntriesResponse = _reflection.GeneratedProtocolMessageType('CountEntriesResponse', (_message.Message,), {
  'DESCRIPTOR' : _COUNTENTRIESRESPONSE,
  '__module__' : 'spire.api.server.entry.v1.entry_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.CountEntriesResponse)
  })
_sym_db.RegisterMessage(CountEntriesResponse)

ListEntriesRequest = _reflection.GeneratedProtocolMessageType('ListEntriesRequest', (_message.Message,), {

  'Filter' : _reflection.GeneratedProtocolMessageType('Filter', (_message.Message,), {
    'DESCRIPTOR' : _LISTENTRIESREQUEST_FILTER,
    '__module__' : 'spire.api.server.entry.v1.entry_pb2'
    # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.ListEntriesRequest.Filter)
    })
  ,
  'DESCRIPTOR' : _LISTENTRIESREQUEST,
  '__module__' : 'spire.api.server.entry.v1.entry_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.ListEntriesRequest)
  })
_sym_db.RegisterMessage(ListEntriesRequest)
_sym_db.RegisterMessage(ListEntriesRequest.Filter)

ListEntriesResponse = _reflection.GeneratedProtocolMessageType('ListEntriesResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTENTRIESRESPONSE,
  '__module__' : 'spire.api.server.entry.v1.entry_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.ListEntriesResponse)
  })
_sym_db.RegisterMessage(ListEntriesResponse)

GetEntryRequest = _reflection.GeneratedProtocolMessageType('GetEntryRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETENTRYREQUEST,
  '__module__' : 'spire.api.server.entry.v1.entry_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.GetEntryRequest)
  })
_sym_db.RegisterMessage(GetEntryRequest)

BatchCreateEntryRequest = _reflection.GeneratedProtocolMessageType('BatchCreateEntryRequest', (_message.Message,), {
  'DESCRIPTOR' : _BATCHCREATEENTRYREQUEST,
  '__module__' : 'spire.api.server.entry.v1.entry_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.BatchCreateEntryRequest)
  })
_sym_db.RegisterMessage(BatchCreateEntryRequest)

BatchCreateEntryResponse = _reflection.GeneratedProtocolMessageType('BatchCreateEntryResponse', (_message.Message,), {

  'Result' : _reflection.GeneratedProtocolMessageType('Result', (_message.Message,), {
    'DESCRIPTOR' : _BATCHCREATEENTRYRESPONSE_RESULT,
    '__module__' : 'spire.api.server.entry.v1.entry_pb2'
    # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.BatchCreateEntryResponse.Result)
    })
  ,
  'DESCRIPTOR' : _BATCHCREATEENTRYRESPONSE,
  '__module__' : 'spire.api.server.entry.v1.entry_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.BatchCreateEntryResponse)
  })
_sym_db.RegisterMessage(BatchCreateEntryResponse)
_sym_db.RegisterMessage(BatchCreateEntryResponse.Result)

BatchUpdateEntryRequest = _reflection.GeneratedProtocolMessageType('BatchUpdateEntryRequest', (_message.Message,), {
  'DESCRIPTOR' : _BATCHUPDATEENTRYREQUEST,
  '__module__' : 'spire.api.server.entry.v1.entry_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.BatchUpdateEntryRequest)
  })
_sym_db.RegisterMessage(BatchUpdateEntryRequest)

BatchUpdateEntryResponse = _reflection.GeneratedProtocolMessageType('BatchUpdateEntryResponse', (_message.Message,), {

  'Result' : _reflection.GeneratedProtocolMessageType('Result', (_message.Message,), {
    'DESCRIPTOR' : _BATCHUPDATEENTRYRESPONSE_RESULT,
    '__module__' : 'spire.api.server.entry.v1.entry_pb2'
    # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.BatchUpdateEntryResponse.Result)
    })
  ,
  'DESCRIPTOR' : _BATCHUPDATEENTRYRESPONSE,
  '__module__' : 'spire.api.server.entry.v1.entry_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.BatchUpdateEntryResponse)
  })
_sym_db.RegisterMessage(BatchUpdateEntryResponse)
_sym_db.RegisterMessage(BatchUpdateEntryResponse.Result)

BatchDeleteEntryRequest = _reflection.GeneratedProtocolMessageType('BatchDeleteEntryRequest', (_message.Message,), {
  'DESCRIPTOR' : _BATCHDELETEENTRYREQUEST,
  '__module__' : 'spire.api.server.entry.v1.entry_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.BatchDeleteEntryRequest)
  })
_sym_db.RegisterMessage(BatchDeleteEntryRequest)

BatchDeleteEntryResponse = _reflection.GeneratedProtocolMessageType('BatchDeleteEntryResponse', (_message.Message,), {

  'Result' : _reflection.GeneratedProtocolMessageType('Result', (_message.Message,), {
    'DESCRIPTOR' : _BATCHDELETEENTRYRESPONSE_RESULT,
    '__module__' : 'spire.api.server.entry.v1.entry_pb2'
    # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.BatchDeleteEntryResponse.Result)
    })
  ,
  'DESCRIPTOR' : _BATCHDELETEENTRYRESPONSE,
  '__module__' : 'spire.api.server.entry.v1.entry_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.BatchDeleteEntryResponse)
  })
_sym_db.RegisterMessage(BatchDeleteEntryResponse)
_sym_db.RegisterMessage(BatchDeleteEntryResponse.Result)

GetAuthorizedEntriesRequest = _reflection.GeneratedProtocolMessageType('GetAuthorizedEntriesRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETAUTHORIZEDENTRIESREQUEST,
  '__module__' : 'spire.api.server.entry.v1.entry_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.GetAuthorizedEntriesRequest)
  })
_sym_db.RegisterMessage(GetAuthorizedEntriesRequest)

GetAuthorizedEntriesResponse = _reflection.GeneratedProtocolMessageType('GetAuthorizedEntriesResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETAUTHORIZEDENTRIESRESPONSE,
  '__module__' : 'spire.api.server.entry.v1.entry_pb2'
  # @@protoc_insertion_point(class_scope:spire.api.server.entry.v1.GetAuthorizedEntriesResponse)
  })
_sym_db.RegisterMessage(GetAuthorizedEntriesResponse)

_ENTRY = DESCRIPTOR.services_by_name['Entry']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'ZGgithub.com/spiffe/spire-api-sdk/proto/spire/api/server/entry/v1;entryv1'
  _COUNTENTRIESREQUEST._serialized_start=228
  _COUNTENTRIESREQUEST._serialized_end=249
  _COUNTENTRIESRESPONSE._serialized_start=251
  _COUNTENTRIESRESPONSE._serialized_end=288
  _LISTENTRIESREQUEST._serialized_start=291
  _LISTENTRIESREQUEST._serialized_end=696
  _LISTENTRIESREQUEST_FILTER._serialized_start=472
  _LISTENTRIESREQUEST_FILTER._serialized_end=696
  _LISTENTRIESRESPONSE._serialized_start=698
  _LISTENTRIESRESPONSE._serialized_end=785
  _GETENTRYREQUEST._serialized_start=787
  _GETENTRYREQUEST._serialized_end=865
  _BATCHCREATEENTRYREQUEST._serialized_start=867
  _BATCHCREATEENTRYREQUEST._serialized_end=982
  _BATCHCREATEENTRYRESPONSE._serialized_start=985
  _BATCHCREATEENTRYRESPONSE._serialized_end=1178
  _BATCHCREATEENTRYRESPONSE_RESULT._serialized_start=1090
  _BATCHCREATEENTRYRESPONSE_RESULT._serialized_end=1178
  _BATCHUPDATEENTRYREQUEST._serialized_start=1181
  _BATCHUPDATEENTRYREQUEST._serialized_end=1344
  _BATCHUPDATEENTRYRESPONSE._serialized_start=1347
  _BATCHUPDATEENTRYRESPONSE._serialized_end=1540
  _BATCHUPDATEENTRYRESPONSE_RESULT._serialized_start=1090
  _BATCHUPDATEENTRYRESPONSE_RESULT._serialized_end=1178
  _BATCHDELETEENTRYREQUEST._serialized_start=1542
  _BATCHDELETEENTRYREQUEST._serialized_end=1580
  _BATCHDELETEENTRYRESPONSE._serialized_start=1583
  _BATCHDELETEENTRYRESPONSE._serialized_end=1749
  _BATCHDELETEENTRYRESPONSE_RESULT._serialized_start=1688
  _BATCHDELETEENTRYRESPONSE_RESULT._serialized_end=1749
  _GETAUTHORIZEDENTRIESREQUEST._serialized_start=1751
  _GETAUTHORIZEDENTRIESREQUEST._serialized_end=1829
  _GETAUTHORIZEDENTRIESRESPONSE._serialized_start=1831
  _GETAUTHORIZEDENTRIESRESPONSE._serialized_end=1902
  _ENTRY._serialized_start=1905
  _ENTRY._serialized_end=2728
# @@protoc_insertion_point(module_scope)
