from flask import Blueprint

admin_bp = Blueprint("admin", __name__)

from app.blueprints.admin.views import dashboard   # noqa: F401, E402
from app.blueprints.admin.views import bookings    # noqa: F401, E402
from app.blueprints.admin.views import artists     # noqa: F401, E402
from app.blueprints.admin.views import works       # noqa: F401, E402
from app.blueprints.admin.views import posts       # noqa: F401, E402
from app.blueprints.admin.views import courses     # noqa: F401, E402
from app.blueprints.admin.views import flash       # noqa: F401, E402
from app.blueprints.admin.views import settings    # noqa: F401, E402
from app.blueprints.admin.views import upload      # noqa: F401, E402
