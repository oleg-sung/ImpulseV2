from app.configuration.routes.routes import *
from app.internal.routes import user

__routes__ = Routes(
    routers=(
        user.router,
    )
)


