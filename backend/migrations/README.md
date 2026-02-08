# Database Migrations

This directory contains SQL migration files for the PostgreSQL database schema.

## Migration Files

Migrations are numbered and executed in order:

1. `001_create_users_table.sql` - Users and authentication
2. `002_create_medications_table.sql` - Medication tracking
3. `003_create_adherence_records_table.sql` - Medication adherence
4. `004_create_appointments_table.sql` - Appointment scheduling
5. `005_create_lab_reports_table.sql` - Lab report storage
6. `006_create_conversations_table.sql` - Chat conversations
7. `007_create_messages_table.sql` - Chat messages
8. `008_create_symptom_analyses_table.sql` - Symptom analysis results
9. `009_create_audit_logs_table.sql` - Security audit trail
10. `010_create_treatment_milestones_table.sql` - Treatment progress tracking
11. `011_create_device_tokens_table.sql` - Push notification tokens

## Running Migrations

### Using Python Script

```bash
cd backend
python migrations/run_migrations.py
```

### Using psql

```bash
psql $DATABASE_URL -f migrations/001_create_users_table.sql
psql $DATABASE_URL -f migrations/002_create_medications_table.sql
# ... continue for all files
```

### Using Docker

```bash
docker-compose exec postgres psql -U postgres -d patient_support -f /migrations/001_create_users_table.sql
```

## Schema Overview

### Core Tables

- **users**: User accounts and authentication
- **medications**: Prescription information
- **adherence_records**: Medication adherence tracking
- **appointments**: Healthcare appointments
- **lab_reports**: Uploaded lab reports and analysis
- **conversations**: Chat conversation sessions
- **messages**: Individual chat messages
- **symptom_analyses**: Symptom checker results
- **audit_logs**: Security and access audit trail
- **treatment_milestones**: Treatment progress tracking
- **device_tokens**: Push notification device registration

### Indexes

All tables include appropriate indexes for:
- Foreign key relationships
- Frequently queried fields
- Date/timestamp fields
- Status fields

### Triggers

Automatic `updated_at` timestamp updates are implemented for tables that track modifications.

## Adding New Migrations

1. Create a new file with the next number: `012_description.sql`
2. Write your SQL DDL statements
3. Test locally before committing
4. Run migrations in order

## Rollback

To rollback migrations, create corresponding `DROP` statements or use database backups.
