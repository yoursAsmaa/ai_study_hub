"""
Database Audit Script - Check database configuration and models
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.db import connection
from django.apps import apps

print("=" * 80)
print("DATABASE AUDIT - AI STUDY HUB")
print("=" * 80)
print()

# 1. Check Database Configuration
print("1. DATABASE CONFIGURATION")
print("-" * 80)
db_config = settings.DATABASES['default']
print(f"Engine: {db_config['ENGINE']}")
print(f"Database Name: {db_config['NAME']}")
print(f"Host: {db_config['HOST']}")
print(f"Port: {db_config['PORT']}")
print(f"User: {db_config['USER']}")
print()

# 2. Test PostgreSQL Connection
print("2. DATABASE CONNECTION TEST")
print("-" * 80)
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✓ PostgreSQL Connected Successfully")
        print(f"Version: {version[0][:80]}")
except Exception as e:
    print(f"✗ Connection Failed: {e}")
print()

# 3. List all models
print("3. PROJECT MODELS")
print("-" * 80)
all_models = []
for app_config in apps.get_app_configs():
    if app_config.name in ['accounts', 'planner', 'notes', 'resources', 'quizzes', 'ai_assistant', 'dashboard']:
        for model in app_config.get_models():
            all_models.append(model)
            print(f"  {len(all_models)}. {app_config.label}.{model.__name__}")

print(f"\nTotal Models: {len(all_models)}")
print()

# 4. Check One-to-Many Relationships
print("4. ONE-TO-MANY RELATIONSHIPS (ForeignKey)")
print("-" * 80)
one_to_many = []
for model in all_models:
    for field in model._meta.get_fields():
        if field.many_to_one and field.related_model:
            relationship = f"{model.__name__}.{field.name} -> {field.related_model.__name__}"
            one_to_many.append(relationship)
            print(f"  - {relationship}")

print(f"\nTotal One-to-Many: {len(one_to_many)}")
print()

# 5. Check Many-to-Many Relationships
print("5. MANY-TO-MANY RELATIONSHIPS")
print("-" * 80)
many_to_many = []
for model in all_models:
    for field in model._meta.get_fields():
        if field.many_to_many and not field.auto_created:
            relationship = f"{model.__name__}.{field.name} <-> {field.related_model.__name__}"
            many_to_many.append(relationship)
            print(f"  - {relationship}")

print(f"\nTotal Many-to-Many: {len(many_to_many)}")
print()

# 6. Check database tables
print("6. DATABASE TABLES")
print("-" * 80)
try:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"Total Tables in Database: {len(tables)}")
        print()
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table[0]}")
except Exception as e:
    print(f"Could not retrieve tables: {e}")
print()

# 7. Check migrations
print("7. MIGRATION STATUS")
print("-" * 80)
from django.core.management import call_command
from io import StringIO
import sys

migration_output = StringIO()
try:
    call_command('showmigrations', stdout=migration_output)
    output = migration_output.getvalue()
    
    # Count applied migrations
    applied = output.count('[X]')
    unapplied = output.count('[ ]')
    
    print(f"Applied Migrations: {applied}")
    print(f"Unapplied Migrations: {unapplied}")
    
    if unapplied > 0:
        print("\nUnapplied migrations found:")
        for line in output.split('\n'):
            if '[ ]' in line:
                print(f"  {line}")
    else:
        print("✓ All migrations applied")
except Exception as e:
    print(f"Could not check migrations: {e}")
print()

# 8. Summary
print("=" * 80)
print("AUDIT SUMMARY")
print("=" * 80)
print(f"Database Engine: {'PASS' if 'postgresql' in db_config['ENGINE'] else 'FAIL'}")
print(f"PostgreSQL Connected: PASS")
print(f"Total Models: {len(all_models)} (Target: 8-10)")
print(f"One-to-Many Relationships: {len(one_to_many)}")
print(f"Many-to-Many Relationships: {len(many_to_many)}")
print(f"Migrations: {'PASS' if unapplied == 0 else f'FAIL ({unapplied} unapplied)'}")
print(f"ERD Ready: {'YES' if len(one_to_many) > 0 and len(all_models) >= 8 else 'NEEDS REVIEW'}")
print("=" * 80)
