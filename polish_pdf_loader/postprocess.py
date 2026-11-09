from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class PostprocessConfig:
    fix_ligatures: bool = True
    join_hyphens: bool = False
    normalize_whitespace: bool = True


_LIGATURE_MAP = {
    "ﬀ": "ff",
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
}

_MULTI_SPACE = re.compile(r"[ \t]+")
_HYPHEN_JOIN = re.compile(r"-\n(\S)")


def postprocess(text: str, config: PostprocessConfig | None = None) -> str:
    """Apply post-processing transformations to extracted PDF text."""
    if config is None:
        config = PostprocessConfig()

    if config.fix_ligatures:
        for ligature, replacement in _LIGATURE_MAP.items():
            text = text.replace(ligature, replacement)

    # Remove soft hyphens (U+00AD) unconditionally — they are invisible layout hints
    text = text.replace("­", "")

    if config.normalize_whitespace:
        text = _MULTI_SPACE.sub(" ", text)

    if config.join_hyphens:
        text = _HYPHEN_JOIN.sub(r"\1", text)

    return text
