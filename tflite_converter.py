import tensorflow as tf
import numpy as np
import joblib
import json
from config import Config
import logging

logger = logging.getLogger(__name__)

class TFLiteConverter:
    def __init__(self):
        self.model = None
        self.scaler = None
    
    def load_sklearn_model(self):
        """Load the trained scikit-learn model"""
        try:
            self.model = joblib.load(Config.MODEL_PATH)
            self.scaler = joblib.load(Config.SCALER_PATH)
            logger.info("Scikit-learn model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading sklearn model: {e}")
            return False
    
    def create_tensorflow_model(self):
        """Create TensorFlow equivalent of the K-means model"""
        if self.model is None or self.scaler is None:
            raise ValueError("Sklearn model not loaded")
        
        # Get model parameters
        cluster_centers = self.model.cluster_centers_
        scaler_mean = self.scaler.mean_
        scaler_scale = self.scaler.scale_
        
        # Convert to float32 to avoid type mismatch
        cluster_centers = cluster_centers.astype(np.float32)
        scaler_mean = scaler_mean.astype(np.float32)
        scaler_scale = scaler_scale.astype(np.float32)
        
        # Create TensorFlow model
        input_shape = (len(scaler_mean),)
        
        # Define the model
        inputs = tf.keras.Input(shape=input_shape, name='input_features')
        
        # Standardization layer (equivalent to sklearn StandardScaler)
        normalized = tf.keras.layers.Lambda(
            lambda x: (x - scaler_mean) / scaler_scale,
            name='standardization'
        )(inputs)
        
        # K-means prediction layer
        # Calculate distances to each cluster center
        def kmeans_prediction(x):
            # Expand dimensions for broadcasting
            x_expanded = tf.expand_dims(x, axis=1)  # Shape: (batch_size, 1, n_features)
            centers_expanded = tf.expand_dims(cluster_centers, axis=0)  # Shape: (1, n_clusters, n_features)
            
            # Calculate squared Euclidean distances
            distances = tf.reduce_sum(tf.square(x_expanded - centers_expanded), axis=2)
            
            # Return the index of the closest cluster
            predictions = tf.argmin(distances, axis=1)
            
            # Also return distances for confidence scoring
            min_distances = tf.reduce_min(distances, axis=1)
            
            return tf.cast(predictions, tf.float32), min_distances
        
        predictions, distances = tf.keras.layers.Lambda(
            kmeans_prediction,
            name='kmeans_prediction'
        )(normalized)
        
        # Create the model
        tf_model = tf.keras.Model(
            inputs=inputs,
            outputs={'cluster': predictions, 'distance': distances},
            name='worker_performance_kmeans'
        )
        
        return tf_model
    
    def convert_to_tflite(self):
        """Convert the TensorFlow model to TFLite"""
        try:
            # Create TensorFlow model
            tf_model = self.create_tensorflow_model()
            
            # Convert to TFLite
            converter = tf.lite.TFLiteConverter.from_keras_model(tf_model)
            
            # Optimization settings
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_types = [tf.float32]
            
            # Convert
            tflite_model = converter.convert()
            
            # Save the model
            with open(Config.TFLITE_MODEL_PATH, 'wb') as f:
                f.write(tflite_model)
            
            logger.info(f"TFLite model saved to {Config.TFLITE_MODEL_PATH}")
            
            # Create model info for Android
            self._create_model_info()
            
            return True
            
        except Exception as e:
            logger.error(f"Error converting to TFLite: {e}")
            return False
    
    def _create_model_info(self):
        """Create model information file for Android integration"""
        with open(Config.METADATA_PATH, 'r') as f:
            metadata = json.load(f)
        
        # Add TFLite specific information
        tflite_info = {
            **metadata,
            'tflite_model_path': Config.TFLITE_MODEL_PATH,
            'input_shape': [1, len(self.scaler.mean_)],
            'output_shape': [1],
            'input_names': ['input_features'],
            'output_names': ['cluster', 'distance'],
            'feature_order': ['attendance_rate', 'avg_work_hours', 'punctuality_score', 'consistency_score'],
            'scaler_params': {
                'mean': self.scaler.mean_.tolist(),
                'scale': self.scaler.scale_.tolist()
            },
            'cluster_centers': self.model.cluster_centers_.tolist(),
            'performance_mapping': {
                '0': 'Low Performer',
                '1': 'Medium Performer', 
                '2': 'High Performer'
            }
        }
        
        # Save updated metadata
        tflite_metadata_path = 'models/tflite_model_info.json'
        with open(tflite_metadata_path, 'w') as f:
            json.dump(tflite_info, f, indent=2)
        
        logger.info(f"TFLite model info saved to {tflite_metadata_path}")
    
    def test_tflite_model(self, test_data):
        """Test the TFLite model with sample data"""
        try:
            # Load TFLite model
            interpreter = tf.lite.Interpreter(model_path=Config.TFLITE_MODEL_PATH)
            interpreter.allocate_tensors()
            
            # Get input and output tensors
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            logger.info("TFLite Model Details:")
            logger.info(f"Input shape: {input_details[0]['shape']}")
            logger.info(f"Output shape: {output_details[0]['shape']}")
            
            # Test with sample data
            test_input = test_data.astype(np.float32)
            interpreter.set_tensor(input_details[0]['index'], test_input)
            
            # Run inference
            interpreter.invoke()
            
            # Get results
            cluster_output = interpreter.get_tensor(output_details[0]['index'])
            distance_output = interpreter.get_tensor(output_details[1]['index'])
            
            logger.info(f"Test prediction - Cluster: {cluster_output}, Distance: {distance_output}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error testing TFLite model: {e}")
            return False