from converse.executors import Executor, ActionBase
from models import Order


@Executor(action="grocery.add")
class GroceryAddAction(ActionBase):
    def execute(self):
        Order.objects.create(item=self.params['item'], quantity=self.params['quantity'], org=self.user.org)
        self.user.messenger.send("{} was successfully added".format(self.params['item']))
