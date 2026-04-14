from typing import Literal

Provider = Literal["athens", "augusta", "fort_valley", "macon", "milledgeville", "unknown"]

def detect_provider(text: str) -> Provider:
    t = text.lower()

    if "click2govcx" in t or "current charge detail" in t:
        return "athens"
    if "augusta utilities department" in t or "billing cycle comparison" in t:
        return "augusta"
    if "utility commission" in t and "fort valley" in t:
        return "fort_valley"
    if "macon water authority" in t:
        return "macon"
    if "city of milledgeville" in t:
        return "milledgeville"

    return "unknown"
