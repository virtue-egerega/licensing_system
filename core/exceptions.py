class LicenseServiceException(Exception):
    pass


class InvalidLicenseKeyError(LicenseServiceException):
    pass


class LicenseExpiredError(LicenseServiceException):
    pass


class LicenseSuspendedError(LicenseServiceException):
    pass


class LicenseCancelledError(LicenseServiceException):
    pass


class SeatLimitReachedError(LicenseServiceException):
    pass


class ProductNotFoundError(LicenseServiceException):
    pass


class UnauthorizedBrandAccessError(LicenseServiceException):
    pass


class LicenseNotFoundError(LicenseServiceException):
    pass


class LicenseAlreadyExistsError(LicenseServiceException):
    pass


class BrandNotFoundError(LicenseServiceException):
    pass


class ActivationNotFoundError(LicenseServiceException):
    pass
