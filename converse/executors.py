import re
from pydoc import locate


class ClassNameExecutor:
    def __init__(self, prefix="", suffix=""):
        self.prefix = prefix
        self.suffix = suffix

    def execute(self, talk_user, action, params, contexts):
        parts = re.split('\W+|_', action)
        class_name = self.prefix + ''.join([part[0].upper() + part[1:] for part in parts]) + self.suffix
        class_object = locate(class_name)
        if class_object is None:
            return
        action_instance = class_object(talk_user, params, contexts)
        action_instance.execute()
