from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class PreparedEmailSample:
    sample_id: str
    source: str
    source_id: str
    source_uri: str
    original_label: str
    normalized_label: str
    subject: str
    body_text: str
    sender_domain: str
    urls: tuple[str, ...]
    attachment_filenames: tuple[str, ...]
    raw_available: bool
    metadata: Mapping[str, str]

    def __post_init__(self) -> None:
        object.__setattr__(self, "urls", tuple(self.urls))
        object.__setattr__(self, "attachment_filenames", tuple(self.attachment_filenames))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
