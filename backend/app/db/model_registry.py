"""Import all mapped domain models before Alembic reads Base.metadata."""

from app.domains.audit import models as audit_models  # noqa: F401
from app.domains.bookings import models as booking_models  # noqa: F401
from app.domains.catalog import models as catalog_models  # noqa: F401
from app.domains.fares import models as fare_models  # noqa: F401
from app.domains.fleet import models as fleet_models  # noqa: F401
from app.domains.identity import models as identity_models  # noqa: F401
from app.domains.identity import passenger_models as passenger_identity_models  # noqa: F401
from app.domains.organizations import models as organization_models  # noqa: F401
from app.domains.reservations import models as reservation_models  # noqa: F401
from app.domains.support import models as support_models  # noqa: F401
from app.domains.support import passenger_models as passenger_support_models  # noqa: F401
from app.domains.trips import models as trip_models  # noqa: F401
from app.domains.wallet import models as wallet_models  # noqa: F401
