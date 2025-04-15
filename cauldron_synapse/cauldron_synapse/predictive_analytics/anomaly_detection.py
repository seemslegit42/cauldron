"""
Anomaly Detection module for the Predictive Analytics layer
"""

import frappe
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statsmodels.api as sm
from scipy import stats
from sklearn.ensemble import IsolationForest
from pyod.models.knn import KNN
from pyod.models.lof import LOF
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def detect_anomalies():
    """Run anomaly detection for all enabled metrics"""
    try:
        # Get all metrics with anomaly detection enabled
        metrics = frappe.get_all(
            "AnalyticsMetric",
            filters={
                "is_active": 1,
                "enable_anomaly_detection": 1
            },
            fields=["name", "metric_name", "metric_type"]
        )
        
        frappe.logger().info(f"Running anomaly detection for {len(metrics)} metrics")
        
        results = []
        for metric in metrics:
            result = detect_anomalies_for_metric(metric.name)
            results.append({
                "metric": metric.name,
                "metric_name": metric.metric_name,
                "success": result["success"],
                "anomalies_found": result.get("anomalies_found", 0) if result["success"] else 0,
                "error": result.get("error") if not result["success"] else None
            })
        
        return {
            "success": True,
            "metrics_processed": len(metrics),
            "results": results
        }
        
    except Exception as e:
        frappe.log_error(f"Error running anomaly detection: {str(e)}", "Anomaly Detection Error")
        return {
            "success": False,
            "error": str(e)
        }

def detect_anomalies_for_metric(metric):
    """Detect anomalies for a specific metric"""
    try:
        metric_doc = frappe.get_doc("AnalyticsMetric", metric)
        
        frappe.logger().info(f"Detecting anomalies for metric: {metric_doc.metric_name}")
        
        # Get historical data
        historical_data = get_historical_data(metric_doc)
        
        if not historical_data or len(historical_data) < 10:
            return {
                "success": False,
                "error": "Insufficient historical data for anomaly detection"
            }
        
        # Prepare data
        df = prepare_data_for_anomaly_detection(historical_data)
        
        # Detect anomalies using multiple methods
        anomalies = []
        
        # Statistical method (Z-score)
        statistical_anomalies = detect_statistical_anomalies(df)
        anomalies.extend(statistical_anomalies)
        
        # Machine learning method (Isolation Forest)
        ml_anomalies = detect_ml_anomalies(df)
        anomalies.extend(ml_anomalies)
        
        # Time series specific method (Seasonal decomposition)
        ts_anomalies = detect_time_series_anomalies(df)
        anomalies.extend(ts_anomalies)
        
        # Remove duplicates
        unique_anomalies = []
        seen_dates = set()
        for anomaly in anomalies:
            if anomaly["date"] not in seen_dates:
                unique_anomalies.append(anomaly)
                seen_dates.add(anomaly["date"])
        
        # Store anomalies
        store_anomalies(metric_doc, unique_anomalies)
        
        # Publish anomaly events
        if unique_anomalies and metric_doc.publish_to_mythos:
            publish_anomaly_events(metric_doc, unique_anomalies)
        
        return {
            "success": True,
            "anomalies_found": len(unique_anomalies),
            "anomalies": unique_anomalies
        }
        
    except Exception as e:
        frappe.log_error(f"Error detecting anomalies for metric {metric}: {str(e)}", "Anomaly Detection Error")
        return {
            "success": False,
            "error": str(e)
        }

def get_historical_data(metric_doc):
    """Get historical data for a metric"""
    try:
        # This would be implemented to fetch actual historical data
        # For now, return placeholder data with some anomalies
        
        # Generate some realistic sample data
        start_date = datetime.now() - timedelta(days=90)
        dates = [start_date + timedelta(days=i) for i in range(90)]
        
        # Create a trend with seasonality and some noise
        trend = np.linspace(100, 150, 90)  # Upward trend from 100 to 150
        seasonality = 20 * np.sin(np.linspace(0, 6*np.pi, 90))  # Seasonal component
        noise = np.random.normal(0, 5, 90)  # Random noise
        
        values = trend + seasonality + noise
        
        # Add some anomalies
        anomaly_indices = [10, 25, 40, 60, 75]
        for idx in anomaly_indices:
            values[idx] += np.random.choice([-1, 1]) * np.random.uniform(30, 50)
        
        # Create data points
        data = [
            {"date": date.strftime("%Y-%m-%d"), "value": value}
            for date, value in zip(dates, values)
        ]
        
        return data
        
    except Exception as e:
        frappe.log_error(f"Error getting historical data: {str(e)}", "Historical Data Error")
        raise

def prepare_data_for_anomaly_detection(historical_data):
    """Prepare data for anomaly detection"""
    try:
        # Convert to DataFrame
        df = pd.DataFrame(historical_data)
        
        # Convert date strings to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Set date as index
        df = df.set_index('date')
        
        # Ensure data is sorted by date
        df = df.sort_index()
        
        # Resample to daily frequency and forward fill missing values
        df = df.resample('D').mean().fillna(method='ffill')
        
        return df
        
    except Exception as e:
        frappe.log_error(f"Error preparing data for anomaly detection: {str(e)}", "Data Preparation Error")
        raise

def detect_statistical_anomalies(df, z_threshold=3.0):
    """Detect anomalies using statistical methods (Z-score)"""
    try:
        # Calculate Z-scores
        z_scores = np.abs(stats.zscore(df['value']))
        
        # Identify anomalies
        anomaly_indices = np.where(z_scores > z_threshold)[0]
        
        # Create anomaly records
        anomalies = []
        for idx in anomaly_indices:
            date = df.index[idx]
            value = df['value'].iloc[idx]
            z_score = z_scores[idx]
            
            anomalies.append({
                "date": date.strftime("%Y-%m-%d"),
                "value": value,
                "expected_value": None,  # Would be calculated in a real implementation
                "deviation": z_score,
                "method": "Z-score",
                "severity": "High" if z_score > 4 else "Medium",
                "description": f"Statistical anomaly detected with Z-score of {z_score:.2f}"
            })
        
        return anomalies
        
    except Exception as e:
        frappe.log_error(f"Error detecting statistical anomalies: {str(e)}", "Statistical Anomaly Error")
        return []

def detect_ml_anomalies(df, contamination=0.05):
    """Detect anomalies using machine learning methods"""
    try:
        # Reshape data for scikit-learn
        X = df['value'].values.reshape(-1, 1)
        
        # Isolation Forest
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        iso_forest.fit(X)
        iso_forest_pred = iso_forest.predict(X)
        
        # LOF (Local Outlier Factor)
        lof = LOF(contamination=contamination)
        lof.fit(X)
        lof_pred = lof.predict(X)
        
        # KNN (K-Nearest Neighbors)
        knn = KNN(contamination=contamination)
        knn.fit(X)
        knn_pred = knn.predict(X)
        
        # Combine predictions (ensemble approach)
        # -1 indicates anomaly in scikit-learn convention
        ensemble_pred = np.zeros(len(X))
        for i in range(len(X)):
            votes = sum([1 for pred in [iso_forest_pred[i], lof_pred[i], knn_pred[i]] if pred == -1])
            ensemble_pred[i] = -1 if votes >= 2 else 1  # Majority vote
        
        # Identify anomalies
        anomaly_indices = np.where(ensemble_pred == -1)[0]
        
        # Create anomaly records
        anomalies = []
        for idx in anomaly_indices:
            date = df.index[idx]
            value = df['value'].iloc[idx]
            
            # Calculate anomaly scores
            iso_score = iso_forest.decision_function([X[idx]])[0]
            lof_score = lof.decision_function([X[idx]])[0]
            knn_score = knn.decision_function([X[idx]])[0]
            
            # Average score (lower is more anomalous)
            avg_score = (iso_score + lof_score + knn_score) / 3
            
            anomalies.append({
                "date": date.strftime("%Y-%m-%d"),
                "value": value,
                "expected_value": None,  # Would be calculated in a real implementation
                "deviation": abs(avg_score),
                "method": "Machine Learning Ensemble",
                "severity": "High" if abs(avg_score) > 0.8 else "Medium",
                "description": f"Machine learning anomaly detected with score of {abs(avg_score):.2f}"
            })
        
        return anomalies
        
    except Exception as e:
        frappe.log_error(f"Error detecting ML anomalies: {str(e)}", "ML Anomaly Error")
        return []

def detect_time_series_anomalies(df, threshold=2.5):
    """Detect anomalies using time series specific methods"""
    try:
        # Check if we have enough data for seasonal decomposition
        if len(df) < 14:  # Need at least 2 weeks for weekly seasonality
            return []
        
        # Try to infer seasonality
        try:
            # For daily data, use 7 for weekly seasonality
            result = sm.tsa.seasonal_decompose(df['value'], model='additive', period=7)
            
            # Calculate residuals
            residuals = result.resid
            
            # Remove NaN values
            residuals = residuals.dropna()
            
            # Calculate standard deviation of residuals
            residual_std = residuals.std()
            
            # Identify anomalies
            anomaly_indices = np.where(np.abs(residuals) > threshold * residual_std)[0]
            
            # Create anomaly records
            anomalies = []
            for idx in anomaly_indices:
                date = residuals.index[idx]
                value = df.loc[date, 'value']
                expected = value - residuals[idx]
                deviation = residuals[idx]
                
                anomalies.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "value": value,
                    "expected_value": expected,
                    "deviation": abs(deviation),
                    "method": "Seasonal Decomposition",
                    "severity": "High" if abs(deviation) > 3 * residual_std else "Medium",
                    "description": f"Time series anomaly detected with deviation of {abs(deviation):.2f}"
                })
            
            return anomalies
            
        except Exception as e:
            frappe.log_error(f"Error in seasonal decomposition: {str(e)}", "Seasonal Decomposition Error")
            return []
        
    except Exception as e:
        frappe.log_error(f"Error detecting time series anomalies: {str(e)}", "Time Series Anomaly Error")
        return []

def store_anomalies(metric_doc, anomalies):
    """Store detected anomalies in the database"""
    try:
        for anomaly in anomalies:
            # Check if anomaly already exists
            existing_anomaly = frappe.db.exists("Anomaly", {
                "metric": metric_doc.name,
                "anomaly_date": anomaly["date"]
            })
            
            if existing_anomaly:
                # Update existing anomaly
                frappe.db.set_value("Anomaly", existing_anomaly, {
                    "value": anomaly["value"],
                    "expected_value": anomaly["expected_value"],
                    "deviation": anomaly["deviation"],
                    "detection_method": anomaly["method"],
                    "severity": anomaly["severity"],
                    "description": anomaly["description"],
                    "detection_date": datetime.now()
                })
            else:
                # Create new anomaly
                new_anomaly = frappe.new_doc("Anomaly")
                new_anomaly.metric = metric_doc.name
                new_anomaly.anomaly_date = anomaly["date"]
                new_anomaly.value = anomaly["value"]
                new_anomaly.expected_value = anomaly["expected_value"]
                new_anomaly.deviation = anomaly["deviation"]
                new_anomaly.detection_method = anomaly["method"]
                new_anomaly.severity = anomaly["severity"]
                new_anomaly.description = anomaly["description"]
                new_anomaly.detection_date = datetime.now()
                new_anomaly.status = "New"
                new_anomaly.insert()
        
        return True
        
    except Exception as e:
        frappe.log_error(f"Error storing anomalies: {str(e)}", "Anomaly Storage Error")
        return False

def publish_anomaly_events(metric_doc, anomalies):
    """Publish anomaly events to Mythos EDA"""
    try:
        # Implementation would depend on Mythos EDA
        for anomaly in anomalies:
            event_data = {
                "event_type": "anomaly.detected",
                "metric_id": metric_doc.name,
                "metric_name": metric_doc.metric_name,
                "metric_type": metric_doc.metric_type,
                "anomaly_date": anomaly["date"],
                "detection_date": datetime.now().isoformat(),
                "value": anomaly["value"],
                "expected_value": anomaly["expected_value"],
                "deviation": anomaly["deviation"],
                "method": anomaly["method"],
                "severity": anomaly["severity"],
                "description": anomaly["description"]
            }
            
            # Placeholder for Mythos event publishing
            frappe.logger().info(f"Would publish to Mythos: {event_data}")
        
        return True
        
    except Exception as e:
        frappe.log_error(f"Error publishing anomaly events: {str(e)}", "Event Publishing Error")
        return False

def analyze_anomaly(anomaly_id):
    """Analyze an anomaly to determine potential causes"""
    try:
        anomaly_doc = frappe.get_doc("Anomaly", anomaly_id)
        
        frappe.logger().info(f"Analyzing anomaly: {anomaly_doc.name}")
        
        # Get metric details
        metric_doc = frappe.get_doc("AnalyticsMetric", anomaly_doc.metric)
        
        # Get historical data around the anomaly date
        anomaly_date = datetime.strptime(anomaly_doc.anomaly_date, "%Y-%m-%d")
        start_date = (anomaly_date - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = (anomaly_date + timedelta(days=5)).strftime("%Y-%m-%d")
        
        # This would fetch actual historical data in a real implementation
        historical_data = get_historical_data(metric_doc)
        
        # Filter data to the relevant time period
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        # Perform analysis
        analysis_results = {
            "anomaly_id": anomaly_doc.name,
            "metric": metric_doc.name,
            "metric_name": metric_doc.metric_name,
            "anomaly_date": anomaly_doc.anomaly_date,
            "value": anomaly_doc.value,
            "expected_value": anomaly_doc.expected_value,
            "deviation": anomaly_doc.deviation,
            "severity": anomaly_doc.severity,
            "analysis": {
                "trend_before_anomaly": "increasing",  # Would be calculated in a real implementation
                "volatility_before_anomaly": "normal",  # Would be calculated in a real implementation
                "pattern_break": True,  # Would be calculated in a real implementation
                "similar_past_anomalies": [],  # Would be identified in a real implementation
                "potential_causes": [
                    "Seasonal pattern disruption",
                    "Outlier event",
                    "Data collection issue"
                ],  # Would be determined in a real implementation
                "recommended_actions": [
                    "Investigate data collection process",
                    "Check for external events on this date",
                    "Monitor for recurrence"
                ]  # Would be generated in a real implementation
            }
        }
        
        # Update anomaly with analysis results
        anomaly_doc.analysis_results = json.dumps(analysis_results["analysis"])
        anomaly_doc.status = "Analyzed"
        anomaly_doc.save()
        
        return {
            "success": True,
            "analysis": analysis_results
        }
        
    except Exception as e:
        frappe.log_error(f"Error analyzing anomaly {anomaly_id}: {str(e)}", "Anomaly Analysis Error")
        return {
            "success": False,
            "error": str(e)
        }"""
Anomaly Detection module for the Predictive Analytics layer
"""

import frappe
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statsmodels.api as sm
from scipy import stats
from sklearn.ensemble import IsolationForest
from pyod.models.knn import KNN
from pyod.models.lof import LOF
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def detect_anomalies():
    """Run anomaly detection for all enabled metrics"""
    try:
        # Get all metrics with anomaly detection enabled
        metrics = frappe.get_all(
            "AnalyticsMetric",
            filters={
                "is_active": 1,
                "enable_anomaly_detection": 1
            },
            fields=["name", "metric_name", "metric_type"]
        )
        
        frappe.logger().info(f"Running anomaly detection for {len(metrics)} metrics")
        
        results = []
        for metric in metrics:
            result = detect_anomalies_for_metric(metric.name)
            results.append({
                "metric": metric.name,
                "metric_name": metric.metric_name,
                "success": result["success"],
                "anomalies_found": result.get("anomalies_found", 0) if result["success"] else 0,
                "error": result.get("error") if not result["success"] else None
            })
        
        return {
            "success": True,
            "metrics_processed": len(metrics),
            "results": results
        }
        
    except Exception as e:
        frappe.log_error(f"Error running anomaly detection: {str(e)}", "Anomaly Detection Error")
        return {
            "success": False,
            "error": str(e)
        }

def detect_anomalies_for_metric(metric):
    """Detect anomalies for a specific metric"""
    try:
        metric_doc = frappe.get_doc("AnalyticsMetric", metric)
        
        frappe.logger().info(f"Detecting anomalies for metric: {metric_doc.metric_name}")
        
        # Get historical data
        historical_data = get_historical_data(metric_doc)
        
        if not historical_data or len(historical_data) < 10:
            return {
                "success": False,
                "error": "Insufficient historical data for anomaly detection"
            }
        
        # Prepare data
        df = prepare_data_for_anomaly_detection(historical_data)
        
        # Detect anomalies using multiple methods
        anomalies = []
        
        # Statistical method (Z-score)
        statistical_anomalies = detect_statistical_anomalies(df)
        anomalies.extend(statistical_anomalies)
        
        # Machine learning method (Isolation Forest)
        ml_anomalies = detect_ml_anomalies(df)
        anomalies.extend(ml_anomalies)
        
        # Time series specific method (Seasonal decomposition)
        ts_anomalies = detect_time_series_anomalies(df)
        anomalies.extend(ts_anomalies)
        
        # Remove duplicates
        unique_anomalies = []
        seen_dates = set()
        for anomaly in anomalies:
            if anomaly["date"] not in seen_dates:
                unique_anomalies.append(anomaly)
                seen_dates.add(anomaly["date"])
        
        # Store anomalies
        store_anomalies(metric_doc, unique_anomalies)
        
        # Publish anomaly events
        if unique_anomalies and metric_doc.publish_to_mythos:
            publish_anomaly_events(metric_doc, unique_anomalies)
        
        return {
            "success": True,
            "anomalies_found": len(unique_anomalies),
            "anomalies": unique_anomalies
        }
        
    except Exception as e:
        frappe.log_error(f"Error detecting anomalies for metric {metric}: {str(e)}", "Anomaly Detection Error")
        return {
            "success": False,
            "error": str(e)
        }

def get_historical_data(metric_doc):
    """Get historical data for a metric"""
    try:
        # This would be implemented to fetch actual historical data
        # For now, return placeholder data with some anomalies
        
        # Generate some realistic sample data
        start_date = datetime.now() - timedelta(days=90)
        dates = [start_date + timedelta(days=i) for i in range(90)]
        
        # Create a trend with seasonality and some noise
        trend = np.linspace(100, 150, 90)  # Upward trend from 100 to 150
        seasonality = 20 * np.sin(np.linspace(0, 6*np.pi, 90))  # Seasonal component
        noise = np.random.normal(0, 5, 90)  # Random noise
        
        values = trend + seasonality + noise
        
        # Add some anomalies
        anomaly_indices = [10, 25, 40, 60, 75]
        for idx in anomaly_indices:
            values[idx] += np.random.choice([-1, 1]) * np.random.uniform(30, 50)
        
        # Create data points
        data = [
            {"date": date.strftime("%Y-%m-%d"), "value": value}
            for date, value in zip(dates, values)
        ]
        
        return data
        
    except Exception as e:
        frappe.log_error(f"Error getting historical data: {str(e)}", "Historical Data Error")
        raise

def prepare_data_for_anomaly_detection(historical_data):
    """Prepare data for anomaly detection"""
    try:
        # Convert to DataFrame
        df = pd.DataFrame(historical_data)
        
        # Convert date strings to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Set date as index
        df = df.set_index('date')
        
        # Ensure data is sorted by date
        df = df.sort_index()
        
        # Resample to daily frequency and forward fill missing values
        df = df.resample('D').mean().fillna(method='ffill')
        
        return df
        
    except Exception as e:
        frappe.log_error(f"Error preparing data for anomaly detection: {str(e)}", "Data Preparation Error")
        raise

def detect_statistical_anomalies(df, z_threshold=3.0):
    """Detect anomalies using statistical methods (Z-score)"""
    try:
        # Calculate Z-scores
        z_scores = np.abs(stats.zscore(df['value']))
        
        # Identify anomalies
        anomaly_indices = np.where(z_scores > z_threshold)[0]
        
        # Create anomaly records
        anomalies = []
        for idx in anomaly_indices:
            date = df.index[idx]
            value = df['value'].iloc[idx]
            z_score = z_scores[idx]
            
            anomalies.append({
                "date": date.strftime("%Y-%m-%d"),
                "value": value,
                "expected_value": None,  # Would be calculated in a real implementation
                "deviation": z_score,
                "method": "Z-score",
                "severity": "High" if z_score > 4 else "Medium",
                "description": f"Statistical anomaly detected with Z-score of {z_score:.2f}"
            })
        
        return anomalies
        
    except Exception as e:
        frappe.log_error(f"Error detecting statistical anomalies: {str(e)}", "Statistical Anomaly Error")
        return []

def detect_ml_anomalies(df, contamination=0.05):
    """Detect anomalies using machine learning methods"""
    try:
        # Reshape data for scikit-learn
        X = df['value'].values.reshape(-1, 1)
        
        # Isolation Forest
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        iso_forest.fit(X)
        iso_forest_pred = iso_forest.predict(X)
        
        # LOF (Local Outlier Factor)
        lof = LOF(contamination=contamination)
        lof.fit(X)
        lof_pred = lof.predict(X)
        
        # KNN (K-Nearest Neighbors)
        knn = KNN(contamination=contamination)
        knn.fit(X)
        knn_pred = knn.predict(X)
        
        # Combine predictions (ensemble approach)
        # -1 indicates anomaly in scikit-learn convention
        ensemble_pred = np.zeros(len(X))
        for i in range(len(X)):
            votes = sum([1 for pred in [iso_forest_pred[i], lof_pred[i], knn_pred[i]] if pred == -1])
            ensemble_pred[i] = -1 if votes >= 2 else 1  # Majority vote
        
        # Identify anomalies
        anomaly_indices = np.where(ensemble_pred == -1)[0]
        
        # Create anomaly records
        anomalies = []
        for idx in anomaly_indices:
            date = df.index[idx]
            value = df['value'].iloc[idx]
            
            # Calculate anomaly scores
            iso_score = iso_forest.decision_function([X[idx]])[0]
            lof_score = lof.decision_function([X[idx]])[0]
            knn_score = knn.decision_function([X[idx]])[0]
            
            # Average score (lower is more anomalous)
            avg_score = (iso_score + lof_score + knn_score) / 3
            
            anomalies.append({
                "date": date.strftime("%Y-%m-%d"),
                "value": value,
                "expected_value": None,  # Would be calculated in a real implementation
                "deviation": abs(avg_score),
                "method": "Machine Learning Ensemble",
                "severity": "High" if abs(avg_score) > 0.8 else "Medium",
                "description": f"Machine learning anomaly detected with score of {abs(avg_score):.2f}"
            })
        
        return anomalies
        
    except Exception as e:
        frappe.log_error(f"Error detecting ML anomalies: {str(e)}", "ML Anomaly Error")
        return []

def detect_time_series_anomalies(df, threshold=2.5):
    """Detect anomalies using time series specific methods"""
    try:
        # Check if we have enough data for seasonal decomposition
        if len(df) < 14:  # Need at least 2 weeks for weekly seasonality
            return []
        
        # Try to infer seasonality
        try:
            # For daily data, use 7 for weekly seasonality
            result = sm.tsa.seasonal_decompose(df['value'], model='additive', period=7)
            
            # Calculate residuals
            residuals = result.resid
            
            # Remove NaN values
            residuals = residuals.dropna()
            
            # Calculate standard deviation of residuals
            residual_std = residuals.std()
            
            # Identify anomalies
            anomaly_indices = np.where(np.abs(residuals) > threshold * residual_std)[0]
            
            # Create anomaly records
            anomalies = []
            for idx in anomaly_indices:
                date = residuals.index[idx]
                value = df.loc[date, 'value']
                expected = value - residuals[idx]
                deviation = residuals[idx]
                
                anomalies.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "value": value,
                    "expected_value": expected,
                    "deviation": abs(deviation),
                    "method": "Seasonal Decomposition",
                    "severity": "High" if abs(deviation) > 3 * residual_std else "Medium",
                    "description": f"Time series anomaly detected with deviation of {abs(deviation):.2f}"
                })
            
            return anomalies
            
        except Exception as e:
            frappe.log_error(f"Error in seasonal decomposition: {str(e)}", "Seasonal Decomposition Error")
            return []
        
    except Exception as e:
        frappe.log_error(f"Error detecting time series anomalies: {str(e)}", "Time Series Anomaly Error")
        return []

def store_anomalies(metric_doc, anomalies):
    """Store detected anomalies in the database"""
    try:
        for anomaly in anomalies:
            # Check if anomaly already exists
            existing_anomaly = frappe.db.exists("Anomaly", {
                "metric": metric_doc.name,
                "anomaly_date": anomaly["date"]
            })
            
            if existing_anomaly:
                # Update existing anomaly
                frappe.db.set_value("Anomaly", existing_anomaly, {
                    "value": anomaly["value"],
                    "expected_value": anomaly["expected_value"],
                    "deviation": anomaly["deviation"],
                    "detection_method": anomaly["method"],
                    "severity": anomaly["severity"],
                    "description": anomaly["description"],
                    "detection_date": datetime.now()
                })
            else:
                # Create new anomaly
                new_anomaly = frappe.new_doc("Anomaly")
                new_anomaly.metric = metric_doc.name
                new_anomaly.anomaly_date = anomaly["date"]
                new_anomaly.value = anomaly["value"]
                new_anomaly.expected_value = anomaly["expected_value"]
                new_anomaly.deviation = anomaly["deviation"]
                new_anomaly.detection_method = anomaly["method"]
                new_anomaly.severity = anomaly["severity"]
                new_anomaly.description = anomaly["description"]
                new_anomaly.detection_date = datetime.now()
                new_anomaly.status = "New"
                new_anomaly.insert()
        
        return True
        
    except Exception as e:
        frappe.log_error(f"Error storing anomalies: {str(e)}", "Anomaly Storage Error")
        return False

def publish_anomaly_events(metric_doc, anomalies):
    """Publish anomaly events to Mythos EDA"""
    try:
        # Implementation would depend on Mythos EDA
        for anomaly in anomalies:
            event_data = {
                "event_type": "anomaly.detected",
                "metric_id": metric_doc.name,
                "metric_name": metric_doc.metric_name,
                "metric_type": metric_doc.metric_type,
                "anomaly_date": anomaly["date"],
                "detection_date": datetime.now().isoformat(),
                "value": anomaly["value"],
                "expected_value": anomaly["expected_value"],
                "deviation": anomaly["deviation"],
                "method": anomaly["method"],
                "severity": anomaly["severity"],
                "description": anomaly["description"]
            }
            
            # Placeholder for Mythos event publishing
            frappe.logger().info(f"Would publish to Mythos: {event_data}")
        
        return True
        
    except Exception as e:
        frappe.log_error(f"Error publishing anomaly events: {str(e)}", "Event Publishing Error")
        return False

def analyze_anomaly(anomaly_id):
    """Analyze an anomaly to determine potential causes"""
    try:
        anomaly_doc = frappe.get_doc("Anomaly", anomaly_id)
        
        frappe.logger().info(f"Analyzing anomaly: {anomaly_doc.name}")
        
        # Get metric details
        metric_doc = frappe.get_doc("AnalyticsMetric", anomaly_doc.metric)
        
        # Get historical data around the anomaly date
        anomaly_date = datetime.strptime(anomaly_doc.anomaly_date, "%Y-%m-%d")
        start_date = (anomaly_date - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = (anomaly_date + timedelta(days=5)).strftime("%Y-%m-%d")
        
        # This would fetch actual historical data in a real implementation
        historical_data = get_historical_data(metric_doc)
        
        # Filter data to the relevant time period
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        # Perform analysis
        analysis_results = {
            "anomaly_id": anomaly_doc.name,
            "metric": metric_doc.name,
            "metric_name": metric_doc.metric_name,
            "anomaly_date": anomaly_doc.anomaly_date,
            "value": anomaly_doc.value,
            "expected_value": anomaly_doc.expected_value,
            "deviation": anomaly_doc.deviation,
            "severity": anomaly_doc.severity,
            "analysis": {
                "trend_before_anomaly": "increasing",  # Would be calculated in a real implementation
                "volatility_before_anomaly": "normal",  # Would be calculated in a real implementation
                "pattern_break": True,  # Would be calculated in a real implementation
                "similar_past_anomalies": [],  # Would be identified in a real implementation
                "potential_causes": [
                    "Seasonal pattern disruption",
                    "Outlier event",
                    "Data collection issue"
                ],  # Would be determined in a real implementation
                "recommended_actions": [
                    "Investigate data collection process",
                    "Check for external events on this date",
                    "Monitor for recurrence"
                ]  # Would be generated in a real implementation
            }
        }
        
        # Update anomaly with analysis results
        anomaly_doc.analysis_results = json.dumps(analysis_results["analysis"])
        anomaly_doc.status = "Analyzed"
        anomaly_doc.save()
        
        return {
            "success": True,
            "analysis": analysis_results
        }
        
    except Exception as e:
        frappe.log_error(f"Error analyzing anomaly {anomaly_id}: {str(e)}", "Anomaly Analysis Error")
        return {
            "success": False,
            "error": str(e)
        }