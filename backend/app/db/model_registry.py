"""Import all mapped domain models before Alembic reads Base.metadata."""
from app.domains.audit import models as audit_models  # noqa: F401
from app.domains.identity import models as identity_models  # noqa: F401
from app.domains.organizations import models as organization_models  # noqa: F401
