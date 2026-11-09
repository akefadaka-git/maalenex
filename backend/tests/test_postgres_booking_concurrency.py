def _create_staff_session(db, *, organization_id=None, permission_code="platform.support.manage"):
    user = User(
        login_identifier="synthetic-staff-" + uuid4().hex + "@example.test",
        display_name="Synthetic Staff Reviewer", status="active",
    )
    role = Role(code="synthetic-role-" + uuid4().hex[:12], description="Synthetic test role")
    permission = Permission(code=permission_code, description="Synthetic test permission")
    db.add_all([user, role, permission])
    db.flush()
    db.add_all([
        RolePermission(role_id=role.id, permission_id=permission.id),
        RoleAssignment(
            user_id=user.id, role_id=role.id,
            organization_id=organization_id, assigned_by=user.id,
        ),
    ])
    if organization_id is not None:
        db.add(OrganizationMembership(
            organization_id=organization_id, user_id=user.id,
            membership_status="active",
        ))
    session_token = issue_opaque_token()
    csrf_token = issue_opaque_token()
    now = db.scalar(select(func.now()))
    db.add(StaffSession(
        user_id=user.id, secret_hash=token_digest(session_token),
        csrf_token_hash=token_digest(csrf_token),
        expires_at=now + timedelta(hours=8),
    ))
    db.flush()
    return session_token, csrf_token
