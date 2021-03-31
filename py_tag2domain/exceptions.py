class AdapterConnectionException(Exception):
    pass


class AdapterDBError(Exception):
    pass


class InvalidMeasurementException(Exception):
    pass


class DisallowedTaxonomyModificationException(Exception):
    pass


class InconsistentTaxonomyException(Exception):
    pass


class StaleMeasurementException(Exception):
    pass
