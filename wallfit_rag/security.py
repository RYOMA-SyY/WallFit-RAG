"""Input sanitization (aligned with Wallfit notebook)."""

from __future__ import annotations

import re

INJECTION_PATTERNS = [
    r"ignore (all |previous |above |prior )?instructions?",
    r"forget (all |previous |your )?instructions?",
    r"you are now",
    r"act as (a |an )?(different|new|another|unrestricted|jailbroken)?",
    r"pretend (you are|to be)",
    r"your new (role|persona|instructions?|task|job)",
    r"disregard (your|all|previous)",
    r"override (your|the|all)",
    r"(developer|admin|god|root|sudo|system) mode",
    r"jailbreak",
    r"dan mode",
    r"do anything now",
    r"<\|?(system|user|assistant|im_start|im_end)\|?>",
    r"###\s*(system|instruction|prompt|context)",
    r"\[INST\]|\[/INST\]",
    r"<<SYS>>|<</SYS>>",
    r"repeat (after me|the (above|following|system|context))",
    r"print (your|the|all) (system |initial |original )?prompt",
    r"reveal (your|the) (instructions?|prompt|system message)",
    r"what (is|are) your (instructions?|prompt|guidelines|rules)",
    r"show (me )?your (system|hidden|secret) prompt",
    r"output (everything|all) (above|before|prior)",
    r"(write|generate|create) (malware|exploit|virus|hack)",
    r"(how to|how do i) (hack|bypass|crack|exploit)",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


class SecurityError(Exception):
    pass


def sanitize_query(query: str, max_query_length: int) -> str:
    if not isinstance(query, str):
        raise SecurityError("Input must be a string.")
    if len(query) > max_query_length:
        raise SecurityError(
            f"Query too long ({len(query)} chars). Max: {max_query_length}."
        )
    for pattern in COMPILED_PATTERNS:
        if pattern.search(query):
            raise SecurityError("Potential prompt injection detected.")
    cleaned = re.sub(r"[<>\[\]{}|]", "", query)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
