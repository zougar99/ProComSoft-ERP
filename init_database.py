# -*- coding: utf-8 -*-
"""
Simple script to initialize the database
"""
from database import Base, engine

print("Initializing database...")
try:
    Base.metadata.create_all(engine)
    print("Database initialized successfully!")
    print("All tables created.")
except Exception as e:
    print("Error: " + str(e))
    import traceback
    traceback.print_exc()

