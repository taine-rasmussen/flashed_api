from enum import Enum

class GradeStyle(str, Enum):
    VSCALE = "VScale"
    FONT = "Font"


# -------------------------------------------------
# Master conversion table
# -------------------------------------------------

CONVERSION_TABLE = [
    {"internal": 0,  "font": "4",   "v": "V0"},
    {"internal": 1,  "font": "4+",  "v": "V0"},
    {"internal": 2,  "font": "5",   "v": "V1"},
    {"internal": 3,  "font": "5+",  "v": "V2"},
    {"internal": 4,  "font": "6A",  "v": "V3"},
    {"internal": 5,  "font": "6A+", "v": "V3"},
    {"internal": 6,  "font": "6B",  "v": "V4"},
    {"internal": 7,  "font": "6B+", "v": "V4"},
    {"internal": 8,  "font": "6C",  "v": "V5"},
    {"internal": 9,  "font": "6C+","v": "V5"},
    {"internal": 10, "font": "7A",  "v": "V6"},
    {"internal": 11, "font": "7A+","v": "V7"},
    {"internal": 12, "font": "7B",  "v": "V8"},
    {"internal": 13, "font": "7B+","v": "V8"},
    {"internal": 14, "font": "7C",  "v": "V9"},
    {"internal": 15, "font": "7C+","v": "V10"},
    {"internal": 16, "font": "8A",  "v": "V11"},
    {"internal": 17, "font": "8A+","v": "V12"},
    {"internal": 18, "font": "8B",  "v": "V13"},
    {"internal": 19, "font": "8B+","v": "V14"},
    {"internal": 20, "font": "8C",  "v": "V15"},
    {"internal": 21, "font": "8C+","v": "V16"},
    {"internal": 22, "font": "9A",  "v": "V17"}
]


# -------------------------------------------------
# Conversion functions
# -------------------------------------------------

def convert_grade_to_internal(grade: str, scale: GradeStyle) -> int:
    """
    Converts a user-entered grade (like "V8" or "7B+") into
    the internal integer value.
    """
    for row in CONVERSION_TABLE:
        if scale == GradeStyle.VSCALE and row["v"] == grade:
            return row["internal"]
        if scale == GradeStyle.FONT and row["font"] == grade:
            return row["internal"]
    raise ValueError(f"Unknown grade '{grade}' for scale '{scale}'")


def convert_internal_to_display(internal: int, scale: GradeStyle) -> str:
    """
    Converts the internal stored grade integer into the
    user-facing grade string for the requested scale.
    """
    for row in CONVERSION_TABLE:
        if row["internal"] == internal:
            if scale == GradeStyle.VSCALE:
                return row["v"]
            elif scale == GradeStyle.FONT:
                return row["font"]
    raise ValueError(f"Cannot find mapping for internal value '{internal}'")
