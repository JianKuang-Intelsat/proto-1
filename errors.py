

class Error(Exception):
    pass

class DirectoryExists(Error):
    pass

class FileNotFound(Error):
    pass
