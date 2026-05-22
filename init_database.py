<<<<<<< HEAD
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

=======
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

>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
