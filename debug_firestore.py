#!/usr/bin/env python3
"""
Script untuk debug dan cek data Firestore
"""

from firebase_client import FirebaseClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_firestore_data():
    """Debug data di Firestore"""
    try:
        # Initialize Firebase client
        firebase_client = FirebaseClient()
        
        # Check users collection
        logger.info("=== CHECKING USERS COLLECTION ===")
        users_ref = firebase_client.db.collection('users')
        users = list(users_ref.limit(3).stream())
        
        logger.info(f"Found {len(users)} users (showing first 3):")
        for user in users:
            logger.info(f"User ID: {user.id}")
            logger.info(f"User data: {user.to_dict()}")
            logger.info("-" * 30)
        
        # Check attendance collection
        logger.info("\n=== CHECKING ATTENDANCE COLLECTION ===")
        attendance_ref = firebase_client.db.collection('attendance')
        
        # Get total count (approximate)
        all_attendance = list(attendance_ref.limit(10).stream())
        logger.info(f"Found {len(all_attendance)} attendance records (showing first 10):")
        
        for i, attendance in enumerate(all_attendance):
            logger.info(f"Attendance {i+1}:")
            logger.info(f"  ID: {attendance.id}")
            data = attendance.to_dict()
            logger.info(f"  Data: {data}")
            
            # Check date format
            if 'date' in data:
                logger.info(f"  Date format: {type(data['date'])} - {data['date']}")
            logger.info("-" * 30)
        
        # Check collections list
        logger.info("\n=== AVAILABLE COLLECTIONS ===")
        collections = firebase_client.db.collections()
        for collection in collections:
            logger.info(f"Collection: {collection.id}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error debugging Firestore: {e}")
        return False

if __name__ == "__main__":
    debug_firestore_data()