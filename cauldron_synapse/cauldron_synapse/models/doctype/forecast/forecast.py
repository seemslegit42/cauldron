"""
Forecast DocType module
"""

import frappe
from frappe.model.document import Document
import json
from datetime import datetime

class Forecast(Document):
    """
    Forecast represents a time-series forecast for a metric
    """
    
    def validate(self):
        """Validate the forecast configuration"""
        self.validate_metric()
        self.validate_model_parameters()
        
    def validate_metric(self):
        """Validate that the metric exists and is suitable for forecasting"""
        if not frappe.db.exists("AnalyticsMetric", self.metric):
            frappe.throw(f"Metric {self.metric} does not exist")
            
        metric_doc = frappe.get_doc("AnalyticsMetric", self.metric)
        if not metric_doc.time_dimension or metric_doc.time_dimension == "None":
            frappe.throw(f"Metric {self.metric} does not have a time dimension and cannot be forecasted")
    
    def validate_model_parameters(self):
        """Validate model parameters"""
        if self.model_parameters:
            try:
                params = json.loads(self.model_parameters)
                if not isinstance(params, dict):
                    frappe.throw("Model parameters must be a valid JSON object")
            except json.JSONDecodeError:
                frappe.throw("Model parameters must be valid JSON")
    
    def before_save(self):
        """Set metadata before saving"""
        if not self.created_by:
            self.created_by = frappe.session.user
            
        if not self.creation_date:
            self.creation_date = datetime.now()
            
        self.modified_date = datetime.now()
        
        # Increment version on update
        if self.get_doc_before_save():
            self.version = (self.version or 1) + 1
    
    def on_update(self):
        """Handle updates to the forecast"""
        if self.status == "Draft" and self.get_doc_before_save() and self.get_doc_before_save().status != "Draft":
            # Reset results if moving back to draft
            self.forecast_values = None
            self.performance_metrics = None
            self.forecast_date = None
            
        self.publish_forecast_updated_event()
        
        if self.status == "Draft" and self.is_active:
            # Schedule forecast generation
            self.schedule_forecast_generation()
    
    def publish_forecast_updated_event(self):
        """Publish event when forecast is updated"""
        if self.publish_to_mythos:
            # Implementation would depend on Mythos EDA
            event_data = {
                "forecast_id": self.name,
                "forecast_name": self.forecast_name,
                "metric": self.metric,
                "status": self.status,
                "updated_by": frappe.session.user,
                "updated_at": datetime.now().isoformat()
            }
            # Placeholder for Mythos event publishing
            frappe.log_error(f"Would publish to Mythos: {event_data}", "Forecast Update")
    
    def schedule_forecast_generation(self):
        """Schedule generation of the forecast"""
        if self.is_active and self.status == "Draft":
            # Implementation would depend on the scheduler being used
            frappe.enqueue(
                "cauldron_synapse.predictive_analytics.forecasting.generate_forecast",
                forecast=self.name,
                queue="long",
                timeout=1500
            )
            
            # Update status to Running
            self.db_set("status", "Running")
    
    def generate_forecast(self):
        """Generate the forecast"""
        try:
            # Update status to Running
            self.db_set("status", "Running")
            
            # Get historical data for the metric
            metric_doc = frappe.get_doc("AnalyticsMetric", self.metric)
            historical_data = self.get_historical_data(metric_doc)
            
            if not historical_data or len(historical_data) < 2:
                frappe.throw("Insufficient historical data for forecasting")
            
            # Determine last historical date
            last_date = max(point["date"] for point in historical_data)
            self.db_set("last_historical_date", last_date)
            
            # Generate forecast based on model type
            forecast_data = self.run_forecast_model(historical_data)
            
            # Calculate performance metrics
            performance_metrics = self.calculate_performance_metrics(historical_data, forecast_data)
            
            # Update document with results
            self.db_set("forecast_values", json.dumps(forecast_data))
            self.db_set("performance_metrics", json.dumps(performance_metrics))
            self.db_set("forecast_date", datetime.now())
            self.db_set("status", "Completed")
            
            # Publish event if configured
            if self.publish_to_mythos:
                self.publish_forecast_completed_event(forecast_data, performance_metrics)
                
            # Trigger automated actions if enabled
            if self.enable_automated_actions:
                self.trigger_automated_actions(forecast_data)
                
            return {
                "success": True,
                "forecast": forecast_data,
                "performance": performance_metrics
            }
            
        except Exception as e:
            self.db_set("status", "Failed")
            frappe.log_error(f"Error generating forecast {self.name}: {str(e)}", "Forecast Generation Error")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_historical_data(self, metric_doc):
        """Get historical data for the metric"""
        # This would be implemented to fetch actual historical data
        # For now, return placeholder data
        return [
            {"date": "2023-01-01", "value": 100},
            {"date": "2023-01-02", "value": 110},
            {"date": "2023-01-03", "value": 120},
            {"date": "2023-01-04", "value": 115},
            {"date": "2023-01-05", "value": 125}
        ]
    
    def run_forecast_model(self, historical_data):
        """Run the forecast model"""
        # This would be implemented with actual forecasting algorithms
        # For now, return placeholder forecast data
        return [
            {"date": "2023-01-06", "value": 130, "lower_bound": 120, "upper_bound": 140},
            {"date": "2023-01-07", "value": 135, "lower_bound": 125, "upper_bound": 145},
            {"date": "2023-01-08", "value": 140, "lower_bound": 130, "upper_bound": 150}
        ]
    
    def calculate_performance_metrics(self, historical_data, forecast_data):
        """Calculate performance metrics for the forecast"""
        # This would calculate metrics like MAPE, MAE, RMSE, etc.
        # For now, return placeholder metrics
        return {
            "MAPE": 5.2,
            "MAE": 3.8,
            "RMSE": 4.5,
            "R2": 0.85
        }
    
    def publish_forecast_completed_event(self, forecast_data, performance_metrics):
        """Publish event when forecast is completed"""
        # Implementation would depend on Mythos EDA
        event_data = {
            "forecast_id": self.name,
            "forecast_name": self.forecast_name,
            "metric": self.metric,
            "status": "Completed",
            "forecast_date": datetime.now().isoformat(),
            "performance_summary": {
                "MAPE": performance_metrics["MAPE"],
                "accuracy": 100 - performance_metrics["MAPE"]
            },
            "forecast_summary": {
                "horizon": self.forecast_horizon,
                "latest_value": forecast_data[0]["value"],
                "trend": "increasing" if forecast_data[-1]["value"] > forecast_data[0]["value"] else "decreasing"
            }
        }
        # Placeholder for Mythos event publishing
        frappe.log_error(f"Would publish to Mythos: {event_data}", "Forecast Completed")
    
    def trigger_automated_actions(self, forecast_data):
        """Trigger automated actions based on forecast results"""
        # This would implement automated actions like creating recommendations
        # For now, just log the intent
        frappe.log_error(f"Would trigger automated actions for forecast {self.name}", "Forecast Actions")
    
    def approve(self, comments=None):
        """Approve the forecast"""
        if self.status != "Completed":
            frappe.throw("Only completed forecasts can be approved")
            
        self.approval_status = "Approved"
        self.approved_by = frappe.session.user
        self.approval_date = datetime.now()
        
        if comments:
            self.approval_comments = comments
            
        self.save()
        
        # Publish approval event if configured
        if self.publish_to_mythos:
            # Implementation would depend on Mythos EDA
            event_data = {
                "forecast_id": self.name,
                "forecast_name": self.forecast_name,
                "metric": self.metric,
                "approval_status": "Approved",
                "approved_by": self.approved_by,
                "approval_date": self.approval_date.isoformat()
            }
            # Placeholder for Mythos event publishing
            frappe.log_error(f"Would publish to Mythos: {event_data}", "Forecast Approved")
    
    def reject(self, comments=None):
        """Reject the forecast"""
        if self.status != "Completed":
            frappe.throw("Only completed forecasts can be rejected")
            
        self.approval_status = "Rejected"
        self.approved_by = frappe.session.user
        self.approval_date = datetime.now()
        
        if comments:
            self.approval_comments = comments
            
        self.save()
        
        # Publish rejection event if configured
        if self.publish_to_mythos:
            # Implementation would depend on Mythos EDA
            event_data = {
                "forecast_id": self.name,
                "forecast_name": self.forecast_name,
                "metric": self.metric,
                "approval_status": "Rejected",
                "approved_by": self.approved_by,
                "approval_date": self.approval_date.isoformat(),
                "comments": self.approval_comments
            }
            # Placeholder for Mythos event publishing
            frappe.log_error(f"Would publish to Mythos: {event_data}", "Forecast Rejected")
    
    def get_forecast_data(self):
        """Get the forecast data in a structured format"""
        if not self.forecast_values:
            return None
            
        try:
            return json.loads(self.forecast_values)
        except json.JSONDecodeError:
            frappe.log_error(f"Invalid JSON in forecast_values for {self.name}", "Forecast Data Error")
            return None"""
Forecast DocType module
"""

import frappe
from frappe.model.document import Document
import json
from datetime import datetime

class Forecast(Document):
    """
    Forecast represents a time-series forecast for a metric
    """
    
    def validate(self):
        """Validate the forecast configuration"""
        self.validate_metric()
        self.validate_model_parameters()
        
    def validate_metric(self):
        """Validate that the metric exists and is suitable for forecasting"""
        if not frappe.db.exists("AnalyticsMetric", self.metric):
            frappe.throw(f"Metric {self.metric} does not exist")
            
        metric_doc = frappe.get_doc("AnalyticsMetric", self.metric)
        if not metric_doc.time_dimension or metric_doc.time_dimension == "None":
            frappe.throw(f"Metric {self.metric} does not have a time dimension and cannot be forecasted")
    
    def validate_model_parameters(self):
        """Validate model parameters"""
        if self.model_parameters:
            try:
                params = json.loads(self.model_parameters)
                if not isinstance(params, dict):
                    frappe.throw("Model parameters must be a valid JSON object")
            except json.JSONDecodeError:
                frappe.throw("Model parameters must be valid JSON")
    
    def before_save(self):
        """Set metadata before saving"""
        if not self.created_by:
            self.created_by = frappe.session.user
            
        if not self.creation_date:
            self.creation_date = datetime.now()
            
        self.modified_date = datetime.now()
        
        # Increment version on update
        if self.get_doc_before_save():
            self.version = (self.version or 1) + 1
    
    def on_update(self):
        """Handle updates to the forecast"""
        if self.status == "Draft" and self.get_doc_before_save() and self.get_doc_before_save().status != "Draft":
            # Reset results if moving back to draft
            self.forecast_values = None
            self.performance_metrics = None
            self.forecast_date = None
            
        self.publish_forecast_updated_event()
        
        if self.status == "Draft" and self.is_active:
            # Schedule forecast generation
            self.schedule_forecast_generation()
    
    def publish_forecast_updated_event(self):
        """Publish event when forecast is updated"""
        if self.publish_to_mythos:
            # Implementation would depend on Mythos EDA
            event_data = {
                "forecast_id": self.name,
                "forecast_name": self.forecast_name,
                "metric": self.metric,
                "status": self.status,
                "updated_by": frappe.session.user,
                "updated_at": datetime.now().isoformat()
            }
            # Placeholder for Mythos event publishing
            frappe.log_error(f"Would publish to Mythos: {event_data}", "Forecast Update")
    
    def schedule_forecast_generation(self):
        """Schedule generation of the forecast"""
        if self.is_active and self.status == "Draft":
            # Implementation would depend on the scheduler being used
            frappe.enqueue(
                "cauldron_synapse.predictive_analytics.forecasting.generate_forecast",
                forecast=self.name,
                queue="long",
                timeout=1500
            )
            
            # Update status to Running
            self.db_set("status", "Running")
    
    def generate_forecast(self):
        """Generate the forecast"""
        try:
            # Update status to Running
            self.db_set("status", "Running")
            
            # Get historical data for the metric
            metric_doc = frappe.get_doc("AnalyticsMetric", self.metric)
            historical_data = self.get_historical_data(metric_doc)
            
            if not historical_data or len(historical_data) < 2:
                frappe.throw("Insufficient historical data for forecasting")
            
            # Determine last historical date
            last_date = max(point["date"] for point in historical_data)
            self.db_set("last_historical_date", last_date)
            
            # Generate forecast based on model type
            forecast_data = self.run_forecast_model(historical_data)
            
            # Calculate performance metrics
            performance_metrics = self.calculate_performance_metrics(historical_data, forecast_data)
            
            # Update document with results
            self.db_set("forecast_values", json.dumps(forecast_data))
            self.db_set("performance_metrics", json.dumps(performance_metrics))
            self.db_set("forecast_date", datetime.now())
            self.db_set("status", "Completed")
            
            # Publish event if configured
            if self.publish_to_mythos:
                self.publish_forecast_completed_event(forecast_data, performance_metrics)
                
            # Trigger automated actions if enabled
            if self.enable_automated_actions:
                self.trigger_automated_actions(forecast_data)
                
            return {
                "success": True,
                "forecast": forecast_data,
                "performance": performance_metrics
            }
            
        except Exception as e:
            self.db_set("status", "Failed")
            frappe.log_error(f"Error generating forecast {self.name}: {str(e)}", "Forecast Generation Error")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_historical_data(self, metric_doc):
        """Get historical data for the metric"""
        # This would be implemented to fetch actual historical data
        # For now, return placeholder data
        return [
            {"date": "2023-01-01", "value": 100},
            {"date": "2023-01-02", "value": 110},
            {"date": "2023-01-03", "value": 120},
            {"date": "2023-01-04", "value": 115},
            {"date": "2023-01-05", "value": 125}
        ]
    
    def run_forecast_model(self, historical_data):
        """Run the forecast model"""
        # This would be implemented with actual forecasting algorithms
        # For now, return placeholder forecast data
        return [
            {"date": "2023-01-06", "value": 130, "lower_bound": 120, "upper_bound": 140},
            {"date": "2023-01-07", "value": 135, "lower_bound": 125, "upper_bound": 145},
            {"date": "2023-01-08", "value": 140, "lower_bound": 130, "upper_bound": 150}
        ]
    
    def calculate_performance_metrics(self, historical_data, forecast_data):
        """Calculate performance metrics for the forecast"""
        # This would calculate metrics like MAPE, MAE, RMSE, etc.
        # For now, return placeholder metrics
        return {
            "MAPE": 5.2,
            "MAE": 3.8,
            "RMSE": 4.5,
            "R2": 0.85
        }
    
    def publish_forecast_completed_event(self, forecast_data, performance_metrics):
        """Publish event when forecast is completed"""
        # Implementation would depend on Mythos EDA
        event_data = {
            "forecast_id": self.name,
            "forecast_name": self.forecast_name,
            "metric": self.metric,
            "status": "Completed",
            "forecast_date": datetime.now().isoformat(),
            "performance_summary": {
                "MAPE": performance_metrics["MAPE"],
                "accuracy": 100 - performance_metrics["MAPE"]
            },
            "forecast_summary": {
                "horizon": self.forecast_horizon,
                "latest_value": forecast_data[0]["value"],
                "trend": "increasing" if forecast_data[-1]["value"] > forecast_data[0]["value"] else "decreasing"
            }
        }
        # Placeholder for Mythos event publishing
        frappe.log_error(f"Would publish to Mythos: {event_data}", "Forecast Completed")
    
    def trigger_automated_actions(self, forecast_data):
        """Trigger automated actions based on forecast results"""
        # This would implement automated actions like creating recommendations
        # For now, just log the intent
        frappe.log_error(f"Would trigger automated actions for forecast {self.name}", "Forecast Actions")
    
    def approve(self, comments=None):
        """Approve the forecast"""
        if self.status != "Completed":
            frappe.throw("Only completed forecasts can be approved")
            
        self.approval_status = "Approved"
        self.approved_by = frappe.session.user
        self.approval_date = datetime.now()
        
        if comments:
            self.approval_comments = comments
            
        self.save()
        
        # Publish approval event if configured
        if self.publish_to_mythos:
            # Implementation would depend on Mythos EDA
            event_data = {
                "forecast_id": self.name,
                "forecast_name": self.forecast_name,
                "metric": self.metric,
                "approval_status": "Approved",
                "approved_by": self.approved_by,
                "approval_date": self.approval_date.isoformat()
            }
            # Placeholder for Mythos event publishing
            frappe.log_error(f"Would publish to Mythos: {event_data}", "Forecast Approved")
    
    def reject(self, comments=None):
        """Reject the forecast"""
        if self.status != "Completed":
            frappe.throw("Only completed forecasts can be rejected")
            
        self.approval_status = "Rejected"
        self.approved_by = frappe.session.user
        self.approval_date = datetime.now()
        
        if comments:
            self.approval_comments = comments
            
        self.save()
        
        # Publish rejection event if configured
        if self.publish_to_mythos:
            # Implementation would depend on Mythos EDA
            event_data = {
                "forecast_id": self.name,
                "forecast_name": self.forecast_name,
                "metric": self.metric,
                "approval_status": "Rejected",
                "approved_by": self.approved_by,
                "approval_date": self.approval_date.isoformat(),
                "comments": self.approval_comments
            }
            # Placeholder for Mythos event publishing
            frappe.log_error(f"Would publish to Mythos: {event_data}", "Forecast Rejected")
    
    def get_forecast_data(self):
        """Get the forecast data in a structured format"""
        if not self.forecast_values:
            return None
            
        try:
            return json.loads(self.forecast_values)
        except json.JSONDecodeError:
            frappe.log_error(f"Invalid JSON in forecast_values for {self.name}", "Forecast Data Error")
            return None