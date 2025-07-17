#!/usr/bin/env python3
"""
Main script for training K-means worker performance analysis model
"""

import os
import sys
import logging
from datetime import datetime

# Import our modules
from firebase_client import FirebaseClient
from data_processor import DataProcessor
from kmeans_model import WorkerKMeansModel
from tflite_converter import TFLiteConverter
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main training pipeline"""
    logger.info("Starting Worker Performance Analysis Model Training")
    
    try:
        # Step 1: Initialize Firebase client
        logger.info("Step 1: Initializing Firebase client...")
        firebase_client = FirebaseClient()
        
        # Step 2: Fetch data from Firestore
        logger.info("Step 2: Fetching data from Firestore...")
        result = firebase_client.get_worker_performance_data()
        
        if not result:
            logger.error("No data returned from Firestore. Please check your database.")
            return False
        
        if len(result) != 2:
            logger.error("Invalid data structure returned from Firestore.")
            return False
            
        workers_df, attendance_df = result
        
        if workers_df.empty:
            logger.error("No workers data found in Firestore.")
            return False
            
        if attendance_df.empty:
            logger.error("No attendance data found in Firestore.")
            logger.info("Please check:")
            logger.info("1. Collection name is 'attendance'")
            logger.info("2. Date field format is 'YYYY-MM-DD'")
            logger.info("3. There are attendance records in the last 30 days")
            return False
        
        logger.info(f"Found {len(workers_df)} workers and {len(attendance_df)} attendance records")
        
        # Step 3: Process data
        logger.info("Step 3: Processing worker performance data...")
        data_processor = DataProcessor()
        processed_data = data_processor.process_worker_data(workers_df, attendance_df)
        
        if processed_data.empty:
            logger.error("No processed data available for training")
            return False
        
        # Step 4: Prepare features for clustering
        logger.info("Step 4: Preparing features for clustering...")
        feature_matrix, feature_names = data_processor.get_feature_matrix()
        
        logger.info(f"Feature matrix shape: {feature_matrix.shape}")
        logger.info(f"Features: {feature_names}")
        
        # Step 5: Train K-means model
        logger.info("Step 5: Training K-means clustering model...")
        kmeans_model = WorkerKMeansModel()
        cluster_labels = kmeans_model.train_model(feature_matrix, feature_names)
        
        # Step 6: Assign performance labels
        logger.info("Step 6: Assigning performance labels...")
        final_data, performance_mapping = kmeans_model.assign_performance_labels(
            processed_data, cluster_labels
        )
        
        # Step 7: Create visualizations
        logger.info("Step 7: Creating visualizations...")
        kmeans_model.visualize_clusters(final_data)
        
        # Step 8: Save the model
        logger.info("Step 8: Saving the trained model...")
        kmeans_model.save_model()
        
        # Step 9: Convert to TFLite
        logger.info("Step 9: Converting model to TensorFlow Lite...")
        tflite_converter = TFLiteConverter()
        
        if tflite_converter.load_sklearn_model():
            if tflite_converter.convert_to_tflite():
                logger.info("TFLite conversion successful!")
                
                # Test the TFLite model
                logger.info("Step 10: Testing TFLite model...")
                test_sample = feature_matrix[:1]  # Use first sample for testing
                tflite_converter.test_tflite_model(test_sample)
            else:
                logger.error("TFLite conversion failed")
                return False
        else:
            logger.error("Failed to load sklearn model for conversion")
            return False
        
        # Step 11: Display results summary
        logger.info("Step 11: Training completed successfully!")
        display_results_summary(final_data, performance_mapping)
        
        return True
        
    except Exception as e:
        logger.error(f"Training failed with error: {e}")
        return False

def display_results_summary(final_data, performance_mapping):
    """Display training results summary"""
    logger.info("\n" + "="*50)
    logger.info("TRAINING RESULTS SUMMARY")
    logger.info("="*50)
    
    # Performance distribution
    performance_counts = final_data['performance_label'].value_counts()
    logger.info("\nPerformance Distribution:")
    for label, count in performance_counts.items():
        percentage = (count / len(final_data)) * 100
        logger.info(f"  {label}: {count} workers ({percentage:.1f}%)")
    
    # Cluster mapping
    logger.info("\nCluster to Performance Mapping:")
    for cluster_id, label in performance_mapping.items():
        logger.info(f"  Cluster {cluster_id}: {label}")
    
    # Feature statistics by performance level
    logger.info("\nAverage Features by Performance Level:")
    feature_cols = ['attendance_rate', 'avg_work_hours', 'punctuality_score', 'consistency_score']
    stats = final_data.groupby('performance_label')[feature_cols].mean()
    
    for performance_level in stats.index:
        logger.info(f"\n  {performance_level}:")
        for feature in feature_cols:
            value = stats.loc[performance_level, feature]
            logger.info(f"    {feature}: {value:.2f}")
    
    # Files created
    logger.info("\nFiles Created:")
    logger.info(f"  - Model: {Config.MODEL_PATH}")
    logger.info(f"  - Scaler: {Config.SCALER_PATH}")
    logger.info(f"  - TFLite Model: {Config.TFLITE_MODEL_PATH}")
    logger.info(f"  - Metadata: {Config.METADATA_PATH}")
    logger.info(f"  - TFLite Info: models/tflite_model_info.json")
    logger.info(f"  - Visualization: cluster_visualization.png")
    logger.info(f"  - Training Log: training.log")

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("Training pipeline completed successfully!")
        sys.exit(0)
    else:
        logger.error("Training pipeline failed!")
        sys.exit(1)