from passlib.context import CryptContext
from enum import Enum
from .conversion import convert_internal_to_display


class GradeStyle(str, Enum):
    VSCALE = "VScale"
    FONT = "Font"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def format_for_display(
    internal_grade: int,
    original_scale: str,
    gym_ranges: list[dict],
    user_pref: GradeStyle,
) -> str:
    # 1) If it was logged as a custom gym-range, convert both endpoints
    if original_scale == "Gym" and gym_ranges:
        # find the matching band
        band = next(b for b in gym_ranges if b["lo"] <= internal_grade <= b["hi"])
        lo_label = convert_internal_to_display(band["lo"], user_pref)
        hi_label = convert_internal_to_display(band["hi"], user_pref)
        return f"{lo_label}–{hi_label}"

    # 2) Otherwise it’s a single point—just convert that one value
    return convert_internal_to_display(internal_grade, user_pref)
