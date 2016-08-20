class Collector(object):
    def initial_parameters(self, db):
        """ Given the DB return the initial parameters to be passed to the collector....
            for example to tell him where to start
            :rtype: dict
            :type db: TinyDB
        """
        return dict()

    def run(self, callback, **params):
        raise NotImplementedError("Collectors should define what to do on run method")


class DuplicateFound(BaseException):
    pass
