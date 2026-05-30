import pyodbc
import logging
from config import build_connection_string

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseHandler:
    """Centralized database handler for MS SQL Server using pyodbc."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseHandler, cls).__new__(cls)
            cls._instance.connection_string = build_connection_string()
        return cls._instance

    def get_connection(self):
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

    def execute_query(self, query, params=None, fetch=False):
        """Executes a query and optionally fetches results."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = True
                
            return result
        except Exception as e:
            logger.error(f"Query execution error: {e}\nQuery: {query}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def execute_scalar(self, query, params=None):
        """Executes a query and returns the first value of the first row."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Scalar query error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def execute_transaction(self, queries_with_params):
        """
        Executes multiple queries in a single transaction.
        queries_with_params: List of (query_string, params_tuple)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            for query, params in queries_with_params:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
