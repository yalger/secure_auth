from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.core.security import get_password_hash


def create_default_admin(db: Session):

    # 检查是否已有 admin 用户
    admin_user = db.query(User).filter_by(username="admin").first()
    if admin_user:
        return

    # 获取 admin 角色
    admin_role = db.query(Role).filter_by(name="admin").first()
    if not admin_role:
        return

    # 创建默认管理员
    admin_user = User(
        username="admin",
        email="alice01007@qq.com",
        password_hash=get_password_hash("Admin@123"),
        is_active=True,
    )

    admin_user.roles.append(admin_role)

    db.add(admin_user)
    db.commit()

    print("Default admin created: username=admin password=Admin@123")
    print("⚠ Please change default admin password after first login!")

def init_seed_data(db: Session):

    # 1. 创建权限
    permissions_data = [
        "user:create",
        "user:read",
        "user:update",
        "user:delete",
    ]

    permissions = []
    for name in permissions_data:
        permission = db.query(Permission).filter_by(name=name).first()
        if not permission:
            permission = Permission(name=name)
            db.add(permission)
        permissions.append(permission)

    db.commit()

    # 2. 创建角色
    admin_role = db.query(Role).filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Super Admin")
        db.add(admin_role)

    user_role = db.query(Role).filter_by(name="user").first()
    if not user_role:
        user_role = Role(name="user", description="Normal User")
        db.add(user_role)

    db.commit()

    # 3. 绑定权限
    if not admin_role.permissions:
        admin_role.permissions = permissions
    if not user_role.permissions:
        user_role.permissions = [
            p for p in permissions if p.name == "user:read"
        ]

    db.commit()

    create_default_admin(db=db)

    print("Seed data initialized.")