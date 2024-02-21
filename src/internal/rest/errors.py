from fastapi import HTTPException


class ClubNameAlreadyExists(HTTPException):
    def __init__(self, detail="Club name726 already exists"):
        super().__init__(status_code=400, detail=detail)


class DocumentNotFound(HTTPException):
    def __init__(self, detail="Document not found"):
        super().__init__(status_code=404, detail=detail)


class CoachNotFound(HTTPException):
    def __init__(self, detail="Coach not found"):
        super().__init__(status_code=404, detail=detail)


class PermissionDenied(HTTPException):
    def __init__(self, detail="Permission denied"):
        super().__init__(status_code=400, detail=detail)


class UserNotFound(HTTPException):
    def __init__(self, detail="User not found"):
        super().__init__(status_code=404, detail=detail)
