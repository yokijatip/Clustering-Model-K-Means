import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Firebase configuration
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
    
    # Date range configuration
    START_DATE = '2025-01-01'  # Format: YYYY-MM-DD
    END_DATE = '2025-12-31'    # Format: YYYY-MM-DD
    
    # Model configuration
    N_CLUSTERS = 3
    CLUSTER_LABELS = {
        0: 'Low Performer',
        1: 'Medium Performer', 
        2: 'High Performer'
    }
    
    # Feature weights for clustering
    FEATURE_WEIGHTS = {
        'attendance_rate': 0.3,
        'avg_work_hours': 0.25,
        'punctuality_score': 0.25,
        'consistency_score': 0.2
    }
    
    # Model paths
    MODEL_PATH = 'models/kmeans_worker_model.joblib'
    SCALER_PATH = 'models/scaler.joblib'
    TFLITE_MODEL_PATH = 'models/worker_analysis_model.tflite'
    METADATA_PATH = 'models/model_metadata.json'