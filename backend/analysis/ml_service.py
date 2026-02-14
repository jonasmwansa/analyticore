"""
Machine Learning Service for AnalytiCore
Complete ML pipeline: training, evaluation, clustering, feature importance
Uses scikit-learn - completely FREE and offline
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import pickle
import os
import json
from datetime import datetime

# Scikit-learn imports
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc
)

# Regression models
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR

# Classification models
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

# Clustering
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score

# Dimensionality reduction
from sklearn.decomposition import PCA

# Feature importance
from sklearn.inspection import permutation_importance


class MLService:
    """Complete ML service for training, evaluation, and predictions"""
    
    REGRESSION_MODELS = {
        'linear_regression': LinearRegression,
        'ridge': Ridge,
        'lasso': Lasso,
        'elastic_net': ElasticNet,
        'random_forest_regressor': RandomForestRegressor,
        'gradient_boosting_regressor': GradientBoostingRegressor,
        'svr': SVR
    }
    
    CLASSIFICATION_MODELS = {
        'logistic_regression': LogisticRegression,
        'random_forest_classifier': RandomForestClassifier,
        'gradient_boosting_classifier': GradientBoostingClassifier,
        'svc': SVC,
        'knn': KNeighborsClassifier,
        'decision_tree': DecisionTreeClassifier
    }
    
    def __init__(self, df: pd.DataFrame, project_id: str, storage_path: str):
        self.df = df
        self.project_id = project_id
        self.storage_path = storage_path
        self.models_dir = os.path.join(storage_path, 'models', project_id)
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Identify column types
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    def prepare_data(self, target_col: str, feature_cols: List[str] = None, 
                     test_size: float = 0.2) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str]]:
        """Prepare data for ML training"""
        
        # Use all numeric columns except target if not specified
        if feature_cols is None:
            feature_cols = [c for c in self.numeric_cols if c != target_col]
        
        # Filter to only include columns that exist
        feature_cols = [c for c in feature_cols if c in self.df.columns]
        
        if not feature_cols:
            raise ValueError("No valid feature columns found")
        
        # Create feature matrix
        X = self.df[feature_cols].copy()
        y = self.df[target_col].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Handle categorical features with encoding
        for col in X.columns:
            if X[col].dtype == 'object':
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
        
        # Handle target encoding for classification
        if y.dtype == 'object':
            le = LabelEncoder()
            y = le.fit_transform(y.astype(str))
        else:
            y = y.fillna(y.mean())
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        return X_train, X_test, y_train, y_test, feature_cols
    
    def train_model(self, model_type: str, algorithm: str, target_col: str,
                    feature_cols: List[str] = None, test_size: float = 0.2,
                    hyperparameters: dict = None) -> Dict[str, Any]:
        """Train a regression or classification model"""
        
        # Validate model type
        if model_type == 'regression':
            if algorithm not in self.REGRESSION_MODELS:
                raise ValueError(f"Unknown regression algorithm: {algorithm}")
            ModelClass = self.REGRESSION_MODELS[algorithm]
        elif model_type == 'classification':
            if algorithm not in self.CLASSIFICATION_MODELS:
                raise ValueError(f"Unknown classification algorithm: {algorithm}")
            ModelClass = self.CLASSIFICATION_MODELS[algorithm]
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Prepare data
        X_train, X_test, y_train, y_test, used_features = self.prepare_data(
            target_col, feature_cols, test_size
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Initialize and train model
        params = hyperparameters or {}
        
        # Set default params for certain models
        if algorithm in ['random_forest_regressor', 'random_forest_classifier']:
            params.setdefault('n_estimators', 100)
            params.setdefault('random_state', 42)
        elif algorithm in ['gradient_boosting_regressor', 'gradient_boosting_classifier']:
            params.setdefault('n_estimators', 100)
            params.setdefault('random_state', 42)
        elif algorithm == 'logistic_regression':
            params.setdefault('max_iter', 1000)
            params.setdefault('random_state', 42)
        elif algorithm == 'svc':
            params.setdefault('probability', True)
            params.setdefault('random_state', 42)
        
        model = ModelClass(**params)
        model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        y_train_pred = model.predict(X_train_scaled)
        
        # Calculate metrics
        if model_type == 'regression':
            metrics = self._calculate_regression_metrics(y_test, y_pred, y_train, y_train_pred)
        else:
            metrics = self._calculate_classification_metrics(y_test, y_pred, model, X_test_scaled)
        
        # Calculate feature importance
        feature_importance = self._get_feature_importance(
            model, X_train_scaled, y_train, used_features, model_type
        )
        
        # Cross-validation score
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
        metrics['cv_score_mean'] = round(float(cv_scores.mean()), 4)
        metrics['cv_score_std'] = round(float(cv_scores.std()), 4)
        
        # Save model
        model_id = f"{algorithm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = os.path.join(self.models_dir, f"{model_id}.pkl")
        
        model_data = {
            'model': model,
            'scaler': scaler,
            'features': used_features,
            'target': target_col,
            'model_type': model_type,
            'algorithm': algorithm
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        return {
            'model_id': model_id,
            'model_type': model_type,
            'algorithm': algorithm,
            'target': target_col,
            'features': used_features,
            'metrics': metrics,
            'feature_importance': feature_importance,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'created_at': datetime.now().isoformat()
        }
    
    def _calculate_regression_metrics(self, y_test, y_pred, y_train, y_train_pred) -> Dict[str, float]:
        """Calculate regression metrics"""
        return {
            'mse': round(float(mean_squared_error(y_test, y_pred)), 4),
            'rmse': round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4),
            'mae': round(float(mean_absolute_error(y_test, y_pred)), 4),
            'r2_score': round(float(r2_score(y_test, y_pred)), 4),
            'train_r2': round(float(r2_score(y_train, y_train_pred)), 4),
            'mape': round(float(np.mean(np.abs((y_test - y_pred) / (y_test + 1e-10))) * 100), 2)
        }
    
    def _calculate_classification_metrics(self, y_test, y_pred, model, X_test_scaled) -> Dict[str, Any]:
        """Calculate classification metrics"""
        metrics = {
            'accuracy': round(float(accuracy_score(y_test, y_pred)), 4),
            'precision': round(float(precision_score(y_test, y_pred, average='weighted', zero_division=0)), 4),
            'recall': round(float(recall_score(y_test, y_pred, average='weighted', zero_division=0)), 4),
            'f1_score': round(float(f1_score(y_test, y_pred, average='weighted', zero_division=0)), 4)
        }
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        # ROC curve for binary classification
        unique_classes = np.unique(y_test)
        if len(unique_classes) == 2 and hasattr(model, 'predict_proba'):
            try:
                y_prob = model.predict_proba(X_test_scaled)[:, 1]
                fpr, tpr, _ = roc_curve(y_test, y_prob)
                metrics['roc_auc'] = round(float(auc(fpr, tpr)), 4)
                metrics['roc_curve'] = {
                    'fpr': [round(float(x), 4) for x in fpr[::max(1, len(fpr)//50)]],
                    'tpr': [round(float(x), 4) for x in tpr[::max(1, len(tpr)//50)]]
                }
            except:
                pass
        
        return metrics
    
    def _get_feature_importance(self, model, X_train, y_train, feature_names: List[str], 
                                model_type: str) -> List[Dict[str, Any]]:
        """Calculate feature importance"""
        importance_list = []
        
        # Try to get built-in feature importance
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_).flatten()
            if len(importances) != len(feature_names):
                importances = np.abs(model.coef_[0]) if len(model.coef_.shape) > 1 else np.abs(model.coef_)
        else:
            # Use permutation importance as fallback
            try:
                perm_importance = permutation_importance(model, X_train, y_train, n_repeats=10, random_state=42)
                importances = perm_importance.importances_mean
            except:
                importances = np.ones(len(feature_names)) / len(feature_names)
        
        # Normalize importances
        if len(importances) == len(feature_names):
            total = np.sum(importances) + 1e-10
            for i, (name, imp) in enumerate(zip(feature_names, importances)):
                importance_list.append({
                    'feature': name,
                    'importance': round(float(imp / total), 4),
                    'raw_importance': round(float(imp), 4)
                })
        
        # Sort by importance
        importance_list.sort(key=lambda x: x['importance'], reverse=True)
        
        return importance_list
    
    def predict(self, model_id: str, data: pd.DataFrame = None) -> Dict[str, Any]:
        """Make predictions using a trained model"""
        
        model_path = os.path.join(self.models_dir, f"{model_id}.pkl")
        if not os.path.exists(model_path):
            raise ValueError(f"Model {model_id} not found")
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        model = model_data['model']
        scaler = model_data['scaler']
        features = model_data['features']
        
        # Use provided data or original dataframe
        df = data if data is not None else self.df
        
        # Prepare features
        X = df[features].copy()
        X = X.fillna(X.mean())
        
        # Handle categorical features
        for col in X.columns:
            if X[col].dtype == 'object':
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
        
        # Scale and predict
        X_scaled = scaler.transform(X)
        predictions = model.predict(X_scaled)
        
        return {
            'model_id': model_id,
            'predictions': [round(float(p), 4) if isinstance(p, (float, np.floating)) else int(p) 
                          for p in predictions],
            'count': len(predictions)
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all trained models for this project"""
        models = []
        
        if not os.path.exists(self.models_dir):
            return models
        
        for filename in os.listdir(self.models_dir):
            if filename.endswith('.pkl'):
                model_path = os.path.join(self.models_dir, filename)
                try:
                    with open(model_path, 'rb') as f:
                        model_data = pickle.load(f)
                    
                    models.append({
                        'model_id': filename.replace('.pkl', ''),
                        'algorithm': model_data.get('algorithm', 'unknown'),
                        'model_type': model_data.get('model_type', 'unknown'),
                        'target': model_data.get('target', 'unknown'),
                        'features': model_data.get('features', [])
                    })
                except:
                    pass
        
        return models
    
    def delete_model(self, model_id: str) -> bool:
        """Delete a trained model"""
        model_path = os.path.join(self.models_dir, f"{model_id}.pkl")
        if os.path.exists(model_path):
            os.remove(model_path)
            return True
        return False


class ClusteringService:
    """Clustering analysis service"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    def prepare_features(self, feature_cols: List[str] = None) -> Tuple[np.ndarray, List[str]]:
        """Prepare features for clustering"""
        
        if feature_cols is None:
            feature_cols = self.numeric_cols
        
        feature_cols = [c for c in feature_cols if c in self.numeric_cols]
        
        if len(feature_cols) < 2:
            raise ValueError("Need at least 2 numeric features for clustering")
        
        X = self.df[feature_cols].copy()
        X = X.fillna(X.mean())
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        return X_scaled, feature_cols
    
    def find_optimal_k(self, feature_cols: List[str] = None, max_k: int = 10) -> Dict[str, Any]:
        """Find optimal number of clusters using elbow method"""
        
        X_scaled, used_features = self.prepare_features(feature_cols)
        
        max_k = min(max_k, len(X_scaled) - 1, 15)
        
        inertias = []
        silhouette_scores = []
        k_range = range(2, max_k + 1)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_scaled)
            inertias.append(float(kmeans.inertia_))
            
            labels = kmeans.labels_
            if len(set(labels)) > 1:
                score = silhouette_score(X_scaled, labels)
                silhouette_scores.append(round(float(score), 4))
            else:
                silhouette_scores.append(0)
        
        # Find elbow point (maximum second derivative)
        if len(inertias) >= 3:
            diffs = np.diff(inertias)
            diffs2 = np.diff(diffs)
            elbow_idx = np.argmax(diffs2) + 2
            optimal_k = list(k_range)[elbow_idx] if elbow_idx < len(k_range) else list(k_range)[0]
        else:
            optimal_k = 2
        
        # Also consider silhouette score
        best_silhouette_k = list(k_range)[np.argmax(silhouette_scores)]
        
        return {
            'k_range': list(k_range),
            'inertias': [round(i, 2) for i in inertias],
            'silhouette_scores': silhouette_scores,
            'elbow_k': optimal_k,
            'best_silhouette_k': best_silhouette_k,
            'recommended_k': best_silhouette_k if max(silhouette_scores) > 0.3 else optimal_k
        }
    
    def run_kmeans(self, n_clusters: int, feature_cols: List[str] = None) -> Dict[str, Any]:
        """Run K-Means clustering"""
        
        X_scaled, used_features = self.prepare_features(feature_cols)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        
        # Calculate metrics
        silhouette = silhouette_score(X_scaled, labels) if len(set(labels)) > 1 else 0
        
        # Get cluster centers
        centers = kmeans.cluster_centers_
        
        # PCA for 2D visualization
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        centers_pca = pca.transform(centers)
        
        # Prepare visualization data
        scatter_data = []
        for i in range(len(X_pca)):
            scatter_data.append({
                'x': round(float(X_pca[i, 0]), 4),
                'y': round(float(X_pca[i, 1]), 4),
                'cluster': int(labels[i])
            })
        
        center_data = []
        for i in range(len(centers_pca)):
            center_data.append({
                'x': round(float(centers_pca[i, 0]), 4),
                'y': round(float(centers_pca[i, 1]), 4),
                'cluster': i
            })
        
        # Cluster statistics
        cluster_stats = []
        for c in range(n_clusters):
            mask = labels == c
            cluster_df = self.df[used_features].iloc[mask]
            stats = {
                'cluster': c,
                'size': int(mask.sum()),
                'percentage': round(float(mask.sum() / len(labels) * 100), 1)
            }
            for col in used_features[:5]:  # Limit to first 5 features
                stats[f'{col}_mean'] = round(float(cluster_df[col].mean()), 2)
            cluster_stats.append(stats)
        
        return {
            'n_clusters': n_clusters,
            'labels': [int(l) for l in labels],
            'silhouette_score': round(float(silhouette), 4),
            'inertia': round(float(kmeans.inertia_), 2),
            'features_used': used_features,
            'scatter_data': scatter_data,
            'centers': center_data,
            'cluster_stats': cluster_stats,
            'pca_explained_variance': [round(float(v), 4) for v in pca.explained_variance_ratio_]
        }
    
    def run_dbscan(self, eps: float = 0.5, min_samples: int = 5, 
                   feature_cols: List[str] = None) -> Dict[str, Any]:
        """Run DBSCAN clustering"""
        
        X_scaled, used_features = self.prepare_features(feature_cols)
        
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(X_scaled)
        
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = (labels == -1).sum()
        
        # Silhouette score (excluding noise)
        if n_clusters > 1:
            mask = labels != -1
            if mask.sum() > n_clusters:
                silhouette = silhouette_score(X_scaled[mask], labels[mask])
            else:
                silhouette = 0
        else:
            silhouette = 0
        
        # PCA for visualization
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        scatter_data = []
        for i in range(len(X_pca)):
            scatter_data.append({
                'x': round(float(X_pca[i, 0]), 4),
                'y': round(float(X_pca[i, 1]), 4),
                'cluster': int(labels[i])
            })
        
        return {
            'n_clusters': n_clusters,
            'n_noise': int(n_noise),
            'labels': [int(l) for l in labels],
            'silhouette_score': round(float(silhouette), 4),
            'eps': eps,
            'min_samples': min_samples,
            'features_used': used_features,
            'scatter_data': scatter_data
        }


class PCAService:
    """PCA and dimensionality reduction service"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    def run_pca(self, n_components: int = None, feature_cols: List[str] = None) -> Dict[str, Any]:
        """Run PCA analysis"""
        
        if feature_cols is None:
            feature_cols = self.numeric_cols
        
        feature_cols = [c for c in feature_cols if c in self.numeric_cols]
        
        X = self.df[feature_cols].copy()
        X = X.fillna(X.mean())
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Determine n_components
        if n_components is None:
            n_components = min(len(feature_cols), len(X_scaled), 10)
        
        # Run PCA
        pca = PCA(n_components=n_components)
        X_pca = pca.fit_transform(X_scaled)
        
        # Explained variance
        explained_variance = pca.explained_variance_ratio_
        cumulative_variance = np.cumsum(explained_variance)
        
        # Component loadings
        loadings = []
        for i, component in enumerate(pca.components_):
            component_loadings = []
            for j, (feature, loading) in enumerate(zip(feature_cols, component)):
                component_loadings.append({
                    'feature': feature,
                    'loading': round(float(loading), 4)
                })
            component_loadings.sort(key=lambda x: abs(x['loading']), reverse=True)
            loadings.append({
                'component': f'PC{i+1}',
                'explained_variance': round(float(explained_variance[i]), 4),
                'loadings': component_loadings
            })
        
        # 2D scatter for visualization (first 2 components)
        scatter_data = []
        for i in range(len(X_pca)):
            scatter_data.append({
                'x': round(float(X_pca[i, 0]), 4),
                'y': round(float(X_pca[i, 1]), 4) if n_components > 1 else 0
            })
        
        # Find optimal components (90% variance)
        optimal_n = np.argmax(cumulative_variance >= 0.9) + 1
        if optimal_n == 1 and cumulative_variance[-1] < 0.9:
            optimal_n = len(cumulative_variance)
        
        return {
            'n_components': n_components,
            'explained_variance': [round(float(v), 4) for v in explained_variance],
            'cumulative_variance': [round(float(v), 4) for v in cumulative_variance],
            'optimal_components': int(optimal_n),
            'loadings': loadings,
            'scatter_data': scatter_data,
            'features_used': feature_cols
        }
