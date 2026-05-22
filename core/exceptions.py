class AppException(Exception):
    pass


class NotFoundError(AppException):
    pass


class ValidationError(AppException):
    pass
