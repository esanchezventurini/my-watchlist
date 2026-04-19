from fastapi import HTTPException
from starlette import status


class NotGroupAdminException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a group admin to perform this action",
        )