from src.configuration.routes.routes import *
from src.internal.users import routes as user
from src.internal.task import routes as task
from src.internal.token import routes as token
from src.internal.collection import routes as collection

__routes__ = Routes(
    routers=(
        user.router,
        task.router,
        token.router,
        collection.router,
    )
)
