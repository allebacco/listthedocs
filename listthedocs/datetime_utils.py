from datetime import datetime
from typing import Union

from dateutil.parser import isoparse


def iso8601_to_datetime(iso8601: Union[str, None]) -> Union[datetime, None]:
    if iso8601 is None:
        return None
    return isoparse(iso8601)
