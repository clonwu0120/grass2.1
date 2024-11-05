from enum import Enum
from urllib.parse import urlparse
from typing import Tuple, Optional


class Status(Enum):
    disconnect = 0
    connecting = 1
    connected = 2


def parse_proxy_url(proxy_url: str) -> Tuple[Optional[str], Optional[str], Optional[int], Optional[Tuple[str, str]]]:
    parsed_url = urlparse(proxy_url)

    scheme = parsed_url.scheme if parsed_url.scheme else None
    host = parsed_url.hostname if parsed_url.hostname else None
    port = parsed_url.port if parsed_url.port else None
    auth = None

    if parsed_url.username and parsed_url.password:
        auth = (parsed_url.username, parsed_url.password)

    return scheme, host, port, auth


def parse_line(line):
    line = line.strip()
    if not line:
        return None, None
    if "==" in line:
        user_id, proxy_url = line.split('==')
    else:
        user_id, proxy_url = line, None
    return user_id, proxy_url or None


