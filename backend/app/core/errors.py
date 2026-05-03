from fastapi import HTTPException, status


class SkillLensError(HTTPException):
    def __init__(self, code: str, message: str, http_status: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=http_status, detail={"code": code, "message": message})


def bad_request(code: str, message: str) -> SkillLensError:
    return SkillLensError(code=code, message=message, http_status=status.HTTP_400_BAD_REQUEST)


def unavailable(code: str, message: str) -> SkillLensError:
    return SkillLensError(code=code, message=message, http_status=status.HTTP_503_SERVICE_UNAVAILABLE)


def rate_limited(code: str, message: str) -> SkillLensError:
    return SkillLensError(code=code, message=message, http_status=status.HTTP_429_TOO_MANY_REQUESTS)
