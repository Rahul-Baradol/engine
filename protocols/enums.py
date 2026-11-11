from enum import Enum, auto

class ApplicationProtocol(Enum):
    HTTP11 = "http1.1"
    HTTP2 = "http2"

class TransportLayerProtocol(Enum):
    TLS = "tls"
    UDP = "udp"

class ProtocolParseStatus(Enum):
    NEED_MORE_DATA = "need_more_data"
    UNKNOWN = "unknown"
    UNSUPPORTED = "unsupported"

class HttpOneParseStatus(Enum):
    MISSING_CONTENT_LENGTH = "missing_content_length"
    MISSING_CONTENT_TYPE = "missing_content_type"
    INVALID_CONTENT_LENGTH = "invalid_content_length"
    INVALID_CONTENT_TYPE = "invalid_content_type"
    UNSUPPORTED_CONTENT_TYPE = "unsupported_content_type"
    INVALID_BODY = "invalid_body"