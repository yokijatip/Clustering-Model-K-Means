import firebase_admin
from firebase_admin import credentials, firestore
from config import Config
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirebaseClient:
    def __init__(self):
        """Initialize Firebase client"""
        try:
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            logger.info("Firebase client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            raise
    
    def get_users_data(self):
        """Fetch all users data from Firestore"""
        try:
            users_ref = self.db.collection('users')
            users = users_ref.stream()
            
            users_data = []
            for user in users:
                user_data = user.to_dict()
                user_data['userId'] = user.id
                users_data.append(user_data)
            
            logger.info(f"Fetched {len(users_data)} users")
            return users_data
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []
    
    def get_attendance_data(self):
        """Fetch attendance data from Firestore for the last N days"""
        try:
            # Use configured date range instead of days_back
            start_date = datetime.strptime(Config.START_DATE, '%Y-%m-%d')
            end_date = datetime.strptime(Config.END_DATE, '%Y-%m-%d')
            
            # Debug: Print date range
            logger.info(f"Searching attendance from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            attendance_ref = self.db.collection('attendance')
            
            # Since Firestore uses DatetimeWithNanoseconds, we need to filter differently
            # Convert our datetime to Firestore timestamp format
            start_timestamp = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_timestamp = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Query with timestamp comparison
            query = attendance_ref.where('date', '>=', start_timestamp).where('date', '<=', end_timestamp)
            
            attendance_docs = query.stream()
            
            attendance_data = []
            for doc in attendance_docs:
                attendance_record = doc.to_dict()
                attendance_record['attendanceId'] = doc.id
                
                # Convert DatetimeWithNanoseconds to string for easier processing
                if 'date' in attendance_record and attendance_record['date']:
                    attendance_record['date_string'] = attendance_record['date'].strftime('%Y-%m-%d')
                if 'clockInTime' in attendance_record and attendance_record['clockInTime']:
                    attendance_record['clockInTime_string'] = attendance_record['clockInTime'].strftime('%Y-%m-%d %H:%M:%S')
                if 'clockOutTime' in attendance_record and attendance_record['clockOutTime']:
                    attendance_record['clockOutTime_string'] = attendance_record['clockOutTime'].strftime('%Y-%m-%d %H:%M:%S')
                
                attendance_data.append(attendance_record)
            
            # If no data found with date filter, try without filter
            if not attendance_data:
                logger.warning("No data found with date filter, trying to get recent data...")
                recent_query = attendance_ref.order_by('date', direction=firestore.Query.DESCENDING).limit(100)
                recent_docs = recent_query.stream()
                
                for doc in recent_docs:
                    attendance_record = doc.to_dict()
                    attendance_record['attendanceId'] = doc.id
                    
                    # Convert DatetimeWithNanoseconds to string
                    if 'date' in attendance_record and attendance_record['date']:
                        attendance_record['date_string'] = attendance_record['date'].strftime('%Y-%m-%d')
                        
                        # Check if this record is within our date range
                        record_date = attendance_record['date'].replace(tzinfo=None)
                        if start_date <= record_date <= end_date:
                            if 'clockInTime' in attendance_record and attendance_record['clockInTime']:
                                attendance_record['clockInTime_string'] = attendance_record['clockInTime'].strftime('%Y-%m-%d %H:%M:%S')
                            if 'clockOutTime' in attendance_record and attendance_record['clockOutTime']:
                                attendance_record['clockOutTime_string'] = attendance_record['clockOutTime'].strftime('%Y-%m-%d %H:%M:%S')
                            
                            attendance_data.append(attendance_record)
                
                logger.info(f"Found {len(attendance_data)} attendance records within date range")
            
            logger.info(f"Total fetched: {len(attendance_data)} attendance records")
            
            # Debug: Show sample of processed data
            if attendance_data:
                logger.info("Sample processed attendance:")
                sample = attendance_data[0]
                logger.info(f"  Date: {sample.get('date_string', 'N/A')}")
                logger.info(f"  User ID: {sample.get('userId', 'N/A')}")
                logger.info(f"  Work Minutes: {sample.get('workMinutes', 'N/A')}")
                logger.info(f"  Status: {sample.get('status', 'N/A')}")
            
            return attendance_data
        except Exception as e:
            logger.error(f"Error fetching attendance: {e}")
            return []
            attendance_data.append(attendance_record)
                
            logger.info(f"Found {len(attendance_data)} recent attendance records")
            
            logger.info(f"Fetched {len(attendance_data)} attendance records")
            return attendance_data
        except Exception as e:
            logger.error(f"Error fetching attendance: {e}")
            return []
    
    def get_worker_performance_data(self):
        """Get comprehensive worker performance data"""
        users = self.get_users_data()
        attendance = self.get_attendance_data()
        
        # Convert to DataFrames for easier processing
        users_df = pd.DataFrame(users)
        attendance_df = pd.DataFrame(attendance)
        
        if attendance_df.empty:
            logger.warning("No attendance data found")
            return pd.DataFrame()
        
        # Filter only workers (not admin/HRD)
        workers_df = users_df[users_df['role'] != 'admin'].copy()
        
        return workers_df, attendance_df