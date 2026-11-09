from enum import Enum, auto

class ApplicationProtocol(Enum):
    HTTP11 = auto()
    HTTP2 = auto()

class TransportLayerProtocol(Enum):
    TLS = auto()
    UDP = auto()

class ProtocolParseStatus(Enum):
    NEED_MORE_DATA = auto()
    UNKNOWN = auto()
    UNSUPPORTED = auto()

class HttpOneParseStatus(Enum):
    MISSING_CONTENT_LENGTH = auto()
    MISSING_CONTENT_TYPE = auto()
    INVALID_CONTENT_LENGTH = auto()
    INVALID_CONTENT_TYPE = auto()
    UNSUPPORTED_CONTENT_TYPE = auto()
    INVALID_BODY = auto()