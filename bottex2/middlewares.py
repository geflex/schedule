def check_middleware(middleware):
    if not callable(middleware):
        raise TypeError('middleware must be callable')
