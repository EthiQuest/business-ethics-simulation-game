# Database Migrations

This directory contains database migrations for the EthiQuest project using Alembic.

## Quick Start

1. Create a new migration:
```bash
python scripts/manage_migrations.py create --name "description_of_changes"
```

2. Upgrade database to latest version:
```bash
python scripts/manage_migrations.py upgrade
```

3. Check current database version:
```bash
python scripts/manage_migrations.py current
```

## Common Tasks

### Creating Migrations

Create a new migration after model changes:
```bash
python scripts/manage_migrations.py create --name "add_user_preferences"
```

### Managing Database State

Upgrade to latest version:
```bash
python scripts/manage_migrations.py upgrade
```

Downgrade one version:
```bash
python scripts/manage_migrations.py downgrade
```

Upgrade/Downgrade to specific version:
```bash
python scripts/manage_migrations.py upgrade --revision "20240310_0001"
python scripts/manage_migrations.py downgrade --revision "20240310_0001"
```

### Checking Status

View migration history:
```bash
python scripts/manage_migrations.py history
```

Check current version:
```bash
python scripts/manage_migrations.py current
```

Verify migrations:
```bash
python scripts/manage_migrations.py check
```

## Best Practices

1. Always review auto-generated migrations
2. Test migrations both up and down
3. Keep migrations atomic (one change per migration)
4. Include meaningful descriptions in migration names
5. Back up database before major migrations

## Troubleshooting

### Common Issues

1. **Migration fails to apply**
   - Check database connectivity
   - Verify current database state
   - Review migration script for errors

2. **Auto-generation misses changes**
   - Ensure models are properly imported
   - Check if changes are supported by auto-generation
   - Create manual migration if needed

3. **Conflicts in migration history**
   - Check branch history
   - Resolve conflicts manually if needed
   - Consider squashing migrations

### Recovery Steps

1. If migration fails:
   ```bash
   python scripts/manage_migrations.py downgrade
   # Fix issues
   python scripts/manage_migrations.py upgrade
   ```

2. To reset migration state:
   ```bash
   python scripts/manage_migrations.py downgrade --revision base
   python scripts/manage_migrations.py upgrade
   ```

## Directory Structure

```
alembic/
├── versions/          # Migration scripts
├── env.py            # Environment configuration
├── script.py.mako    # Migration template
└── alembic.ini       # Alembic configuration
```

## Additional Information

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)