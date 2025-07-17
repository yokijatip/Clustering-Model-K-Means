import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.processed_data = None
    
    def calculate_attendance_rate(self, worker_id, attendance_df):
        """Calculate attendance rate for a worker"""
        worker_attendance = attendance_df[attendance_df['userId'] == worker_id]
        
        # Count approved attendance
        approved_days = len(worker_attendance[worker_attendance['status'] == 'approved'])
        
        # Calculate working days from config date range
        working_days = self._calculate_working_days_from_config()
        
        attendance_rate = (approved_days / working_days) * 100 if working_days > 0 else 0
        return min(attendance_rate, 100)  # Cap at 100%
    
    def calculate_avg_work_hours(self, worker_id, attendance_df):
        """Calculate average work hours per day"""
        worker_attendance = attendance_df[
            (attendance_df['userId'] == worker_id) & 
            (attendance_df['status'] == 'approved')
        ]
        
        if worker_attendance.empty:
            return 0
        
        # Convert workMinutes to hours
        work_hours = worker_attendance['workMinutes'] / 60
        return work_hours.mean()
    
    def calculate_punctuality_score(self, worker_id, attendance_df):
        """Calculate punctuality score based on clock in/out times"""
        worker_attendance = attendance_df[
            (attendance_df['userId'] == worker_id) & 
            (attendance_df['status'] == 'approved')
        ]
        
        if worker_attendance.empty:
            return 0
        
        punctual_days = 0
        total_days = len(worker_attendance)
        
        for _, record in worker_attendance.iterrows():
            # Use the string version for easier parsing
            clock_in_time = record.get('clockInTime_string', '')
            clock_out_time = record.get('clockOutTime_string', '')
            
            # Simple punctuality check (can be enhanced)
            if self._is_punctual(clock_in_time, clock_out_time):
                punctual_days += 1
        
        return (punctual_days / total_days) * 100 if total_days > 0 else 0
    
    def calculate_consistency_score(self, worker_id, attendance_df):
        """Calculate work consistency score"""
        worker_attendance = attendance_df[
            (attendance_df['userId'] == worker_id) & 
            (attendance_df['status'] == 'approved')
        ]
        
        if len(worker_attendance) < 2:
            return 0
        
        # Calculate standard deviation of work hours
        work_hours = worker_attendance['workMinutes'] / 60
        std_dev = work_hours.std()
        
        # Convert to consistency score (lower std_dev = higher consistency)
        # Normalize to 0-100 scale
        max_std = 4  # Assume max std deviation of 4 hours
        consistency_score = max(0, (max_std - std_dev) / max_std * 100)
        
        return consistency_score
    
    def process_worker_data(self, workers_df, attendance_df):
        """Process all worker data for clustering"""
        processed_workers = []
        
        for _, worker in workers_df.iterrows():
            worker_id = worker['userId']
            
            # Calculate performance metrics
            attendance_rate = self.calculate_attendance_rate(worker_id, attendance_df)
            avg_work_hours = self.calculate_avg_work_hours(worker_id, attendance_df)
            punctuality_score = self.calculate_punctuality_score(worker_id, attendance_df)
            consistency_score = self.calculate_consistency_score(worker_id, attendance_df)
            
            processed_worker = {
                'userId': worker_id,
                'name': worker.get('name', 'Unknown'),
                'email': worker.get('email', ''),
                'workerId': worker.get('workerId', ''),
                'attendance_rate': attendance_rate,
                'avg_work_hours': avg_work_hours,
                'punctuality_score': punctuality_score,
                'consistency_score': consistency_score,
                'total_records': len(attendance_df[attendance_df['userId'] == worker_id])
            }
            
            processed_workers.append(processed_worker)
        
        self.processed_data = pd.DataFrame(processed_workers)
        logger.info(f"Processed data for {len(processed_workers)} workers")
        
        return self.processed_data
    
    def _calculate_working_days_from_config(self):
        """Calculate working days from config date range excluding weekends"""
        from config import Config
        start_date = datetime.strptime(Config.START_DATE, '%Y-%m-%d')
        end_date = datetime.strptime(Config.END_DATE, '%Y-%m-%d')
        
        working_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            # Monday = 0, Sunday = 6
            if current_date.weekday() < 5:  # Monday to Friday
                working_days += 1
            current_date += timedelta(days=1)
        
        return working_days
    
    def _is_punctual(self, clock_in_time, clock_out_time):
        """Check if worker was punctual (simplified logic)"""
        try:
            # Parse time strings (format: "2024-12-19 09:43:30")
            if not clock_in_time or not clock_out_time:
                return False
            
            # Extract hour from clock in time (format: "2024-12-19 09:43:30")
            time_part = clock_in_time.split(' ')[1]  # Get "09:43:30"
            clock_in_hour = int(time_part.split(':')[0])  # Get hour
            
            # Consider punctual if clocked in before 8 AM (adjust as needed)
            # You can modify this logic based on your company's work hours
            return clock_in_hour <= 7  # Punctual if clock in at 7 AM or earlier
        except:
            return False
    
    def get_feature_matrix(self):
        """Get feature matrix for clustering"""
        if self.processed_data is None:
            raise ValueError("Data not processed yet. Call process_worker_data first.")
        
        features = ['attendance_rate', 'avg_work_hours', 'punctuality_score', 'consistency_score']
        return self.processed_data[features].values, features