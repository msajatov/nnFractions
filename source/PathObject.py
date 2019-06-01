import os, errno


class PathObject:

    def __init__(self, type, parent_dir_name, name=""):
        self.type = type
        self.parent_dir_name = parent_dir_name

        if name:
            self.name = name
            self.path = "{0}/{1}".format(self.parent_dir_name, self.name)
        else:
            self.name = type + "/default"
            self.path = "{0}/{1}".format(self.parent_dir_name, self.name)

    def set_name(self, dir_name):
        if dir_name:
            self.name = dir_name
            self.path = "{0}/{1}".format(self.parent_dir_name, self.name)
            try:
                if not os.path.exists(self.path):
                    os.makedirs(self.path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

    def get_name(self):
        return self.name

    def get_path(self):
        return self.path


class DirPathObject(PathObject):

    def __init__(self, type, parent_dir_name, name=""):
        PathObject.__init__(self, type, parent_dir_name, name)
        if name:
            try:
                if not os.path.exists(self.path):
                    os.makedirs(self.path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

    def set_name(self, dir_name):
        if dir_name:
            self.name = dir_name
            self.path = "{0}/{1}".format(self.parent_dir_name, self.name)
            try:
                if not os.path.exists(self.path):
                    os.makedirs(self.path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise


class FilePathObject(PathObject):

    def __init__(self, type, parent_dir_name, name=""):
        PathObject.__init__(self, type, parent_dir_name, name)

    def set_name(self, dir_name):
        if dir_name:
            self.name = dir_name
            self.path = "{0}/{1}".format(self.parent_dir_name, self.name)

