"""MongoDB connection management"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from ..config import Config
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection singleton"""
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """Connect to MongoDB"""
        if self._client is None:
            try:
                self._client = MongoClient(
                    Config.MONGODB_URI,
                    serverSelectionTimeoutMS=5000,
                    maxPoolSize=50
                )
                # Test connection
                self._client.admin.command('ping')
                
                # Get database name from URI or use default
                db_name = Config.MONGODB_URI.split('/')[-1].split('?')[0] or 'patient_support'
                self._db = self._client[db_name]
                
                logger.info(f"Connected to MongoDB database: {db_name}")
            except ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
        
        return self._db
    
    def get_db(self):
        """Get database instance"""
        if self._db is None:
            return self.connect()
        return self._db
    
    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")


# Global instance
mongodb = MongoDB()


def get_mongodb():
    """Get MongoDB database instance"""
    return mongodb.get_db()
