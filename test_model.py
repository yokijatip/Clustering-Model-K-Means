#!/usr/bin/env python3
"""
Script untuk testing model yang sudah dilatih
"""

import numpy as np
import pandas as pd
import joblib
import json
import tensorflow as tf
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sklearn_model():
    """Test scikit-learn model"""
    try:
        # Load model dan scaler
        model = joblib.load(Config.MODEL_PATH)
        scaler = joblib.load(Config.SCALER_PATH)
        
        # Sample data untuk testing
        sample_data = np.array([
            [95.0, 8.5, 90.0, 85.0],  # High performer
            [75.0, 7.0, 70.0, 60.0],  # Medium performer  
            [50.0, 5.5, 40.0, 30.0]   # Low performer
        ])
        
        # Standardize dan predict
        sample_scaled = scaler.transform(sample_data)
        predictions = model.predict(sample_scaled)
        
        logger.info("Scikit-learn Model Test Results:")
        for i, pred in enumerate(predictions):
            logger.info(f"Sample {i+1}: Cluster {pred}")
            logger.info(f"  Features: {sample_data[i]}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing sklearn model: {e}")
        return False

def test_tflite_model():
    """Test TensorFlow Lite model"""
    try:
        # Load TFLite model
        interpreter = tf.lite.Interpreter(model_path=Config.TFLITE_MODEL_PATH)
        interpreter.allocate_tensors()
        
        # Get input and output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        logger.info("TFLite Model Details:")
        logger.info(f"Input details: {input_details}")
        logger.info(f"Output details: {output_details}")
        
        # Sample data
        sample_data = np.array([[95.0, 8.5, 90.0, 85.0]], dtype=np.float32)
        
        # Set input tensor
        interpreter.set_tensor(input_details[0]['index'], sample_data)
        
        # Run inference
        interpreter.invoke()
        
        # Get output
        cluster_output = interpreter.get_tensor(output_details[0]['index'])
        distance_output = interpreter.get_tensor(output_details[1]['index'])
        
        logger.info("TFLite Model Test Results:")
        logger.info(f"Input: {sample_data}")
        logger.info(f"Predicted Cluster: {cluster_output}")
        logger.info(f"Distance: {distance_output}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing TFLite model: {e}")
        return False

def compare_models():
    """Compare sklearn and TFLite model outputs"""
    try:
        # Load sklearn model
        sklearn_model = joblib.load(Config.MODEL_PATH)
        scaler = joblib.load(Config.SCALER_PATH)
        
        # Load TFLite model
        interpreter = tf.lite.Interpreter(model_path=Config.TFLITE_MODEL_PATH)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Test samples
        test_samples = np.array([
            [95.0, 8.5, 90.0, 85.0],  # High performer
            [75.0, 7.0, 70.0, 60.0],  # Medium performer  
            [50.0, 5.5, 40.0, 30.0],  # Low performer
            [85.0, 8.0, 80.0, 75.0],  # Another high performer
            [65.0, 6.5, 60.0, 55.0]   # Another medium performer
        ])
        
        logger.info("Model Comparison Results:")
        logger.info("-" * 50)
        
        for i, sample in enumerate(test_samples):
            # Sklearn prediction
            sample_scaled = scaler.transform([sample])
            sklearn_pred = sklearn_model.predict(sample_scaled)[0]
            
            # TFLite prediction
            sample_tflite = sample.reshape(1, -1).astype(np.float32)
            interpreter.set_tensor(input_details[0]['index'], sample_tflite)
            interpreter.invoke()
            tflite_pred = interpreter.get_tensor(output_details[0]['index'])[0]
            
            # Compare
            match = "✓" if sklearn_pred == int(tflite_pred) else "✗"
            
            logger.info(f"Sample {i+1}: {sample}")
            logger.info(f"  Sklearn: {sklearn_pred}, TFLite: {int(tflite_pred)} {match}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error comparing models: {e}")
        return False

def load_and_display_metadata():
    """Load and display model metadata"""
    try:
        with open(Config.METADATA_PATH, 'r') as f:
            metadata = json.load(f)
        
        logger.info("Model Metadata:")
        logger.info("-" * 30)
        for key, value in metadata.items():
            logger.info(f"{key}: {value}")
        
        # Load TFLite info if exists
        tflite_info_path = 'models/tflite_model_info.json'
        try:
            with open(tflite_info_path, 'r') as f:
                tflite_info = json.load(f)
            
            logger.info("\nTFLite Model Info:")
            logger.info("-" * 30)
            logger.info(f"Input shape: {tflite_info['input_shape']}")
            logger.info(f"Feature order: {tflite_info['feature_order']}")
            logger.info(f"Performance mapping: {tflite_info['performance_mapping']}")
            
        except FileNotFoundError:
            logger.warning("TFLite model info not found")
        
        return True
        
    except Exception as e:
        logger.error(f"Error loading metadata: {e}")
        return False

def main():
    """Main testing function"""
    logger.info("Starting Model Testing...")
    
    # Test 1: Load and display metadata
    logger.info("\n1. Loading Model Metadata...")
    load_and_display_metadata()
    
    # Test 2: Test sklearn model
    logger.info("\n2. Testing Scikit-learn Model...")
    test_sklearn_model()
    
    # Test 3: Test TFLite model
    logger.info("\n3. Testing TensorFlow Lite Model...")
    test_tflite_model()
    
    # Test 4: Compare models
    logger.info("\n4. Comparing Model Outputs...")
    compare_models()
    
    logger.info("\nTesting completed!")

if __name__ == "__main__":
    main()