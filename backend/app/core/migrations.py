"""Database initialization and utilities"""

import logging
from sqlalchemy import inspect, text
from app.core.database import engine, Base, SessionLocal
from app.models.floor import Floor
from app.models.event import Event

logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """Drop all database tables (Use with caution!)"""
    try:
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


def check_tables_exist() -> bool:
    """Check if tables exist in database"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return len(tables) > 0
    except Exception as e:
        logger.error(f"Error checking tables: {e}")
        return False


def get_table_info():
    """Get information about all tables"""
    try:
        inspector = inspect(engine)
        tables_info = {}
        
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            
            tables_info[table_name] = {
                "columns": [col["name"] for col in columns],
                "indexes": [idx["name"] for idx in indexes],
                "column_count": len(columns),
            }
        
        return tables_info
    except Exception as e:
        logger.error(f"Error getting table info: {e}")
        return {}


def execute_raw_query(query: str, params: dict = None):
    """Execute raw SQL query"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query), params or {})
            connection.commit()
            return result
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise


def get_database_stats():
    """Get database statistics"""
    try:
        session = SessionLocal()
        stats = {
            "floors_count": session.query(Floor).count(),
            "events_count": session.query(Event).count(),
            "tables_exist": check_tables_exist(),
        }
        session.close()
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {}


def reinitialize_database():
    """Completely reinitialize database (drops and recreates)"""
    try:
        logger.warning("REINITIALIZING DATABASE...")
        drop_tables()
        create_tables()
        logger.info("Database reinitialized successfully")
    except Exception as e:
        logger.error(f"Error reinitializing database: {e}")
        raise


if __name__ == "__main__":
    # Initialize logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create tables
    create_tables()
    
    # Display info
    info = get_table_info()
    print("\n=== Database Tables ===")
    for table, details in info.items():
        print(f"\n{table}:")
        print(f"  Columns: {', '.join(details['columns'])}")
        print(f"  Column count: {details['column_count']}")
        
    stats = get_database_stats()
    print(f"\n=== Database Statistics ===")
    print(f"Floors: {stats.get('floors_count', 0)}")
    print(f"Events: {stats.get('events_count', 0)}")
