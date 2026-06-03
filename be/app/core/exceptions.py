class BaseAppException(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class LoadError(BaseAppException):
    status_code = 503
    code = "ML_INITIALIZATION_FAILED"


class SongNotFoundError(BaseAppException):
    status_code = 404
    code = "SONG_NOT_FOUND"

    def __init__(self, song_id: str, message: str):
        self.song_id = song_id
        super().__init__(message)


class InsufficientRecommendationsError(BaseAppException):
    status_code = 422
    code = "INSUFFICIENT_RECOMMENDATIONS"

    def __init__(self, song_id: str, message: str):
        self.song_id = song_id
        super().__init__(message)