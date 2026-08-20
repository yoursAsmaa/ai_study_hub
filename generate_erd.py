"""
ERD Generation Script for AI Study Hub
Generates Entity-Relationship Diagram from Django models
"""
import os
import sys

print("=" * 80)
print("ERD GENERATION FOR AI STUDY HUB")
print("=" * 80)
print()

print("OPTION 1: Using django-extensions (Recommended)")
print("-" * 80)
print("1. Install required packages:")
print("   pip install django-extensions pygraphviz")
print("   OR (if pygraphviz fails):")
print("   pip install django-extensions pydot")
print()
print("2. Add to INSTALLED_APPS in config/settings.py:")
print("   'django_extensions',")
print()
print("3. Generate ERD:")
print("   python manage.py graph_models -a -g -o erd_diagram.png")
print()
print("   Options:")
print("   -a : All apps")
print("   -g : Group by app")
print("   -o : Output file")
print()
print("   For custom apps only:")
print("   python manage.py graph_models accounts planner notes resources quizzes ai_assistant dashboard -g -o erd_custom.png")
print()
print("=" * 80)
print()

print("OPTION 2: Using dbdiagram.io (Manual - Professional)")
print("-" * 80)
print("Visit: https://dbdiagram.io/")
print("Copy the DBML code from: erd_dbml_code.txt")
print("Paste into dbdiagram.io editor")
print("Export as PNG or PDF")
print()
print("=" * 80)
print()

print("OPTION 3: Using ERDAlchemy (Python-based)")
print("-" * 80)
print("1. Install: pip install eralchemy")
print("2. Generate: eralchemy -i 'postgresql://user:password@localhost/ai_study_hub' -o erd.png")
print()
print("=" * 80)
print()

print("GENERATING DBML CODE FOR OPTION 2...")
print()

# Generate DBML code for dbdiagram.io
dbml_code = '''// AI Study Hub - Entity Relationship Diagram
// Generated for Graduation Project

Table User {
  id integer [primary key]
  username varchar [unique]
  email varchar [unique]
  password varchar
  first_name varchar
  last_name varchar
  is_active boolean
  date_joined datetime
}

Table Profile {
  id integer [primary key]
  user_id integer [ref: - User.id, unique]
  profile_image varchar
  bio text
  university varchar
  major varchar
  phone varchar
  is_email_verified boolean
  created_at datetime
  updated_at datetime
}

Table Category {
  id integer [primary key]
  user_id integer [ref: > User.id]
  name varchar
  color varchar
  created_at datetime
  
  indexes {
    (user_id, name) [unique]
  }
}

Table Tag {
  id integer [primary key]
  user_id integer [ref: > User.id]
  name varchar
  
  indexes {
    (user_id, name) [unique]
  }
}

Table Note {
  id integer [primary key]
  user_id integer [ref: > User.id]
  category_id integer [ref: > Category.id, null]
  title varchar
  content text
  summary text
  created_at datetime
  updated_at datetime
}

Table Note_Tags {
  note_id integer [ref: > Note.id]
  tag_id integer [ref: > Tag.id]
  
  indexes {
    (note_id, tag_id) [pk]
  }
}

Table Task {
  id integer [primary key]
  user_id integer [ref: > User.id]
  category_id integer [ref: > Category.id, null]
  title varchar
  description text
  due_date datetime
  priority varchar
  status varchar
  is_completed boolean
  created_at datetime
  updated_at datetime
}

Table Resource {
  id integer [primary key]
  user_id integer [ref: > User.id]
  category_id integer [ref: > Category.id, null]
  title varchar
  description text
  link varchar
  resource_type varchar
  created_at datetime
  updated_at datetime
}

Table Quiz {
  id integer [primary key]
  user_id integer [ref: > User.id]
  source_note_id integer [ref: > Note.id, null]
  title varchar
  score float
  total_questions integer
  correct_answers integer
  completed boolean
  created_at datetime
  updated_at datetime
}

Table Question {
  id integer [primary key]
  quiz_id integer [ref: > Quiz.id]
  question_text text
  options json
  correct_answer varchar
  user_answer varchar
  explanation text
  is_correct boolean
  created_at datetime
}

Table Flashcard {
  id integer [primary key]
  user_id integer [ref: > User.id]
  quiz_id integer [ref: > Quiz.id, null]
  source_note_id integer [ref: > Note.id, null]
  front text
  back text
  known boolean
  created_at datetime
}

Table StudySession {
  id integer [primary key]
  user_id integer [ref: > User.id]
  category_id integer [ref: > Category.id, null]
  subject varchar
  start_time datetime
  end_time datetime
  duration_minutes integer
  notes text
  created_at datetime
}

Table ChatMessage {
  id integer [primary key]
  user_id integer [ref: > User.id]
  role varchar
  content text
  created_at datetime
}

Table Activity {
  id integer [primary key]
  user_id integer [ref: > User.id]
  action_type varchar
  description varchar
  created_at datetime
}
'''

with open('erd_dbml_code.txt', 'w') as f:
    f.write(dbml_code)

print("✓ DBML code saved to: erd_dbml_code.txt")
print()
print("=" * 80)
print("NEXT STEPS:")
print("=" * 80)
print("1. Choose one of the options above")
print("2. For django-extensions: Run the installation and commands")
print("3. For dbdiagram.io: Copy erd_dbml_code.txt content to the website")
print("4. Export as PNG or PDF for graduation project")
print("=" * 80)
