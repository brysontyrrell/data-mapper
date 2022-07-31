from fastapi import Path

PathId = Path(regex=r"^[0-9a-f]{24}$")
