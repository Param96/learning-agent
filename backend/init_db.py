from app.core.database import Base, engine

# Import all models to ensure they're registered

# Create all tables
Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
