import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import json
import os
from config import Config
import logging

logger = logging.getLogger(__name__)

class WorkerKMeansModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.cluster_centers_ = None
        self.labels_ = None
        
    def train_model(self, feature_matrix, feature_names):
        """Train K-means clustering model"""
        self.feature_names = feature_names
        
        # Standardize features
        X_scaled = self.scaler.fit_transform(feature_matrix)
        
        # Train K-means model
        self.model = KMeans(
            n_clusters=Config.N_CLUSTERS,
            random_state=42,
            n_init=10,
            max_iter=300
        )
        
        self.labels_ = self.model.fit_predict(X_scaled)
        self.cluster_centers_ = self.model.cluster_centers_
        
        # Calculate silhouette score
        silhouette_avg = silhouette_score(X_scaled, self.labels_)
        logger.info(f"Silhouette Score: {silhouette_avg:.3f}")
        
        return self.labels_
    
    def predict_cluster(self, feature_matrix):
        """Predict cluster for new data"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        X_scaled = self.scaler.transform(feature_matrix)
        return self.model.predict(X_scaled)
    
    def assign_performance_labels(self, processed_data, cluster_labels):
        """Assign performance labels based on cluster characteristics"""
        processed_data = processed_data.copy()
        processed_data['cluster'] = cluster_labels
        
        # Calculate cluster means for each feature
        cluster_means = processed_data.groupby('cluster')[
            ['attendance_rate', 'avg_work_hours', 'punctuality_score', 'consistency_score']
        ].mean()
        
        # Calculate overall performance score for each cluster
        cluster_scores = {}
        for cluster_id in range(Config.N_CLUSTERS):
            cluster_data = cluster_means.loc[cluster_id]
            
            # Weighted performance score
            score = (
                cluster_data['attendance_rate'] * Config.FEATURE_WEIGHTS['attendance_rate'] +
                min(cluster_data['avg_work_hours'] / 8 * 100, 100) * Config.FEATURE_WEIGHTS['avg_work_hours'] +
                cluster_data['punctuality_score'] * Config.FEATURE_WEIGHTS['punctuality_score'] +
                cluster_data['consistency_score'] * Config.FEATURE_WEIGHTS['consistency_score']
            )
            cluster_scores[cluster_id] = score
        
        # Sort clusters by performance score
        sorted_clusters = sorted(cluster_scores.items(), key=lambda x: x[1])
        
        # Assign labels: lowest score = Low, highest = High
        performance_mapping = {}
        for i, (cluster_id, score) in enumerate(sorted_clusters):
            if i == 0:
                performance_mapping[cluster_id] = 'Low Performer'
            elif i == 1:
                performance_mapping[cluster_id] = 'Medium Performer'
            else:
                performance_mapping[cluster_id] = 'High Performer'
        
        # Add performance labels to data
        processed_data['performance_label'] = processed_data['cluster'].map(performance_mapping)
        
        logger.info("Performance label mapping:")
        for cluster_id, label in performance_mapping.items():
            logger.info(f"Cluster {cluster_id}: {label} (Score: {cluster_scores[cluster_id]:.2f})")
        
        return processed_data, performance_mapping
    
    def visualize_clusters(self, processed_data, save_path='cluster_visualization.png'):
        """Create visualization of clusters"""
        plt.figure(figsize=(15, 10))
        
        # Create subplots for different feature combinations
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Attendance Rate vs Avg Work Hours
        scatter1 = axes[0, 0].scatter(
            processed_data['attendance_rate'], 
            processed_data['avg_work_hours'],
            c=processed_data['cluster'], 
            cmap='viridis', 
            alpha=0.7
        )
        axes[0, 0].set_xlabel('Attendance Rate (%)')
        axes[0, 0].set_ylabel('Average Work Hours')
        axes[0, 0].set_title('Attendance Rate vs Work Hours')
        
        # Plot 2: Punctuality vs Consistency
        scatter2 = axes[0, 1].scatter(
            processed_data['punctuality_score'], 
            processed_data['consistency_score'],
            c=processed_data['cluster'], 
            cmap='viridis', 
            alpha=0.7
        )
        axes[0, 1].set_xlabel('Punctuality Score (%)')
        axes[0, 1].set_ylabel('Consistency Score (%)')
        axes[0, 1].set_title('Punctuality vs Consistency')
        
        # Plot 3: Performance distribution
        performance_counts = processed_data['performance_label'].value_counts()
        axes[1, 0].pie(performance_counts.values, labels=performance_counts.index, autopct='%1.1f%%')
        axes[1, 0].set_title('Performance Distribution')
        
        # Plot 4: Feature comparison by cluster
        cluster_means = processed_data.groupby('performance_label')[
            ['attendance_rate', 'avg_work_hours', 'punctuality_score', 'consistency_score']
        ].mean()
        
        cluster_means.plot(kind='bar', ax=axes[1, 1])
        axes[1, 1].set_title('Average Features by Performance Level')
        axes[1, 1].set_xlabel('Performance Level')
        axes[1, 1].set_ylabel('Score')
        axes[1, 1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info(f"Visualization saved to {save_path}")
    
    def save_model(self):
        """Save trained model and scaler"""
        os.makedirs('models', exist_ok=True)
        
        # Save model and scaler
        joblib.dump(self.model, Config.MODEL_PATH)
        joblib.dump(self.scaler, Config.SCALER_PATH)
        
        # Save metadata
        metadata = {
            'model_type': 'KMeans',
            'n_clusters': Config.N_CLUSTERS,
            'feature_names': self.feature_names,
            'cluster_labels': Config.CLUSTER_LABELS,
            'feature_weights': Config.FEATURE_WEIGHTS,
            'created_at': pd.Timestamp.now().isoformat()
        }
        
        with open(Config.METADATA_PATH, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("Model saved successfully")
    
    def load_model(self):
        """Load trained model and scaler"""
        try:
            self.model = joblib.load(Config.MODEL_PATH)
            self.scaler = joblib.load(Config.SCALER_PATH)
            
            with open(Config.METADATA_PATH, 'r') as f:
                metadata = json.load(f)
                self.feature_names = metadata['feature_names']
            
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False