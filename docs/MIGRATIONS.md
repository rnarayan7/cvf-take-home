# Database Migrations and Seeding

This project uses Alembic for database migrations and a separate seeding system for test data.

## Alembic Migrations

### Setup
Alembic is configured to use your SQLAlchemy models from `src/python/db/schemas.py` and reads the database URL from the `DATABASE_URL` environment variable (defaults to `sqlite:///./cvf.db`).

### Commands

**Generate a new migration (after model changes):**
```bash
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Check current migration status:**
```bash
alembic current
```

**View migration history:**
```bash
alembic history
```

**Downgrade to previous migration:**
```bash
alembic downgrade -1
```

## Database Seeding

### CLI Integration
The seeding system is integrated into the main CLI tool:

**Seed database with sample data:**
```bash
./bin/run.sh --seed
```

**Force recreate seed data (clears existing data first):**
```bash
./bin/run.sh --seed-force
```

**Setup database without starting server:**
```bash
./bin/run.sh --setup-only --seed
```

### Direct Usage
You can also run the seeding script directly:

```bash
# Basic seeding
python src/python/db/seed_data.py

# Force recreate
python src/python/db/seed_data.py --force
```

### Seed Data Structure
The seeding script creates:
- **3 Companies**: Acme Corp, TechStart Inc, GrowthCo
- **6 Cohorts**: With realistic trading terms (sharing percentages, cash caps)
- **6 Payments**: Sample payment data aligned with cohorts
- **4 Thresholds**: Payment thresholds for different companies

## Migration vs Seeding

- **Migrations** (`alembic/`): Handle database schema changes (tables, columns, constraints)
- **Seeding** (`src/python/db/seed_data.py`): Populate database with sample data for development/testing

## Development Workflow

1. **Make model changes** in `src/python/db/schemas.py`
2. **Generate migration**: `alembic revision --autogenerate -m "Add new column"`
3. **Review generated migration** in `alembic/versions/`
4. **Apply migration**: `alembic upgrade head`
5. **Seed database** (if needed): `./bin/run.sh --seed`

## Clean Database Setup

To start with a completely fresh database:

```bash
# Remove existing database
rm cvf.db

# Run migrations to create schema
alembic upgrade head

# Seed with sample data
./bin/run.sh --seed --skip-db-init
```

## Notes

- The seeding script is idempotent - it won't create duplicates if run multiple times
- Use `--seed-force` only when you want to completely reset the data
- All seeding operations are logged with structured logging
- The initial migration includes constraints and indexes from `pg_db_setup.sql`