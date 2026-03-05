from sqlalchemy.orm import Session

from app.models import user
from app.models.audit_log import AuditLog


class AuditService:

    @staticmethod
    def record(
        db: Session,
        action: str,
        status: str,
        user_id: int | None = None,
        username: str | None = None,
        resource: str | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
        detail: dict | None = None
    ):
        log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            resource=resource,
            ip=ip,
            user_agent=user_agent,
            status=status,
            detail=detail
        )

        db.add(log)
        # 只 add，不 commit，事务由外层控制