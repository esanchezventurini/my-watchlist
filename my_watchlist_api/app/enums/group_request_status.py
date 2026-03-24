import enum


class GroupRequestStatus(str, enum.Enum):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3