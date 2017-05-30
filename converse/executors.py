import abc
from inspect import isclass


class ExecutorInner:
    def __init__(self, obj):
        self.obj = obj

    def __call__(self, user, params, contexts):
        if isclass(self.obj):
            instance = self.obj(user=user, params=params, contexts=contexts)
            return instance.execute()
        else:
            return self.obj(user=user, params=params, contexts=contexts)


class Executor:
    action_map = {}

    def __init__(self, action):
        """
        A decorator class that identifies the action on which this object should be called. If the object decorated is
        a class, it should extend `ActionBase` and override the execute method.
        The following arguments are passed to the decorated method:
        1. user: The application user for which this action needs to be executed.
        2. params: a dict (str: str) of parameters parsed from the text
        3. contexts: a dict (str: dict), the outer dict has keys as the name of the contexts the inner dict has
                     key-value pairs for params in these contexts
        When the decorated object is a class, these arguments are passed to the constructor instead
        :param action: The name of the action
        """
        self.action = action

    def __call__(self, obj, *args, **kwargs):
        self.action_map[self.action] = ExecutorInner(obj)
        return self.action_map[self.action]

    @classmethod
    def execute(cls, action, user, params, contexts):
        if action in cls.action_map:
            return cls.action_map[action](user, params, contexts)


class ActionBase:
    __metaclass__ = abc.ABCMeta

    def __init__(self, user, params, contexts):
        self.user = user
        self.params = params
        self.contexts = contexts

    def execute(self):
        pass
