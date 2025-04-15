"""
Main API controller for Synapse module
"""

import frappe
from frappe import _
import json
from datetime import datetime, timedelta

@frappe.whitelist()
def get_status():
    """Get the status of the Synapse module"""
    return {
        "status": "success",
        "message": _("Synapse module is active"),
        "module": "cauldron_synapse",
        "version": frappe.get_module("cauldron_synapse").__version__
    }

@frappe.whitelist()
def get_metrics(filters=None):
    """Get analytics metrics based on filters"""
    try:
        if filters and isinstance(filters, str):
            filters = json.loads(filters)
            
        # Build query conditions
        conditions = "1=1"
        if filters:
            if filters.get("metric_type"):
                conditions += f" AND metric_type = '{filters['metric_type']}'"
            if filters.get("is_active") is not None:
                is_active = 1 if filters["is_active"] else 0
                conditions += f" AND is_active = {is_active}"
            if filters.get("owner_user"):
                conditions += f" AND owner_user = '{filters['owner_user']}'"
            if filters.get("search"):
                conditions += f" AND (metric_name LIKE '%{filters['search']}%' OR description LIKE '%{filters['search']}%')"
        
        # Execute query
        metrics = frappe.db.sql(f"""
            SELECT name, metric_name, metric_type, description, business_domain, 
                   is_active, owner_user, created_date, modified_date
            FROM `tabAnalyticsMetric`
            WHERE {conditions}
            ORDER BY modified_date DESC
        """, as_dict=True)
        
        return {
            "status": "success",
            "metrics": metrics,
            "count": len(metrics)
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_metrics: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_metric_value(metric, filters=None, time_range=None):
    """Get the current value of a metric"""
    try:
        if not frappe.db.exists("AnalyticsMetric", metric):
            return {
                "status": "error",
                "message": f"Metric {metric} does not exist"
            }
            
        metric_doc = frappe.get_doc("AnalyticsMetric", metric)
        
        # Parse filters if provided
        if filters and isinstance(filters, str):
            filters = json.loads(filters)
            
        # Parse time range if provided
        if time_range and isinstance(time_range, str):
            time_range = json.loads(time_range)
        
        # Calculate metric value
        value = metric_doc.calculate_value(filters)
        
        # Check thresholds
        threshold_status = metric_doc.check_thresholds(value)
        
        return {
            "status": "success",
            "metric": {
                "name": metric_doc.name,
                "metric_name": metric_doc.metric_name,
                "metric_type": metric_doc.metric_type,
                "description": metric_doc.description
            },
            "value": value,
            "threshold_status": threshold_status["status"],
            "target": metric_doc.target_value,
            "unit": metric_doc.unit_of_measure,
            "is_percentage": metric_doc.is_percentage,
            "is_currency": metric_doc.is_currency,
            "currency": metric_doc.currency if metric_doc.is_currency else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_metric_value: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_metric_history(metric, start_date=None, end_date=None, granularity="daily"):
    """Get historical values for a metric"""
    try:
        if not frappe.db.exists("AnalyticsMetric", metric):
            return {
                "status": "error",
                "message": f"Metric {metric} does not exist"
            }
            
        metric_doc = frappe.get_doc("AnalyticsMetric", metric)
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().date()
        elif isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            
        if not start_date:
            start_date = end_date - timedelta(days=30)
        elif isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        
        # Get historical values
        history = metric_doc.get_historical_values(start_date, end_date, granularity)
        
        return {
            "status": "success",
            "metric": {
                "name": metric_doc.name,
                "metric_name": metric_doc.metric_name,
                "metric_type": metric_doc.metric_type
            },
            "history": history,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "granularity": granularity
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_metric_history: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_forecasts(filters=None):
    """Get forecasts based on filters"""
    try:
        if filters and isinstance(filters, str):
            filters = json.loads(filters)
            
        # Build query conditions
        conditions = "1=1"
        if filters:
            if filters.get("metric"):
                conditions += f" AND metric = '{filters['metric']}'"
            if filters.get("status"):
                conditions += f" AND status = '{filters['status']}'"
            if filters.get("is_active") is not None:
                is_active = 1 if filters["is_active"] else 0
                conditions += f" AND is_active = {is_active}"
            if filters.get("created_by"):
                conditions += f" AND created_by = '{filters['created_by']}'"
            if filters.get("search"):
                conditions += f" AND (forecast_name LIKE '%{filters['search']}%' OR description LIKE '%{filters['search']}%')"
        
        # Execute query
        forecasts = frappe.db.sql(f"""
            SELECT name, forecast_name, metric, status, forecast_model, 
                   forecast_horizon, forecast_frequency, is_active, 
                   created_by, creation_date, modified_date, approval_status
            FROM `tabForecast`
            WHERE {conditions}
            ORDER BY modified_date DESC
        """, as_dict=True)
        
        return {
            "status": "success",
            "forecasts": forecasts,
            "count": len(forecasts)
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_forecasts: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_forecast_data(forecast):
    """Get detailed forecast data"""
    try:
        if not frappe.db.exists("Forecast", forecast):
            return {
                "status": "error",
                "message": f"Forecast {forecast} does not exist"
            }
            
        forecast_doc = frappe.get_doc("Forecast", forecast)
        
        # Get forecast data
        forecast_data = forecast_doc.get_forecast_data()
        
        # Get performance metrics
        performance_metrics = None
        if forecast_doc.performance_metrics:
            try:
                performance_metrics = json.loads(forecast_doc.performance_metrics)
            except json.JSONDecodeError:
                performance_metrics = None
        
        # Get metric details
        metric_doc = frappe.get_doc("AnalyticsMetric", forecast_doc.metric)
        
        return {
            "status": "success",
            "forecast": {
                "name": forecast_doc.name,
                "forecast_name": forecast_doc.forecast_name,
                "description": forecast_doc.description,
                "status": forecast_doc.status,
                "forecast_model": forecast_doc.forecast_model,
                "forecast_horizon": forecast_doc.forecast_horizon,
                "forecast_frequency": forecast_doc.forecast_frequency,
                "confidence_level": forecast_doc.confidence_level,
                "forecast_date": forecast_doc.forecast_date,
                "last_historical_date": forecast_doc.last_historical_date,
                "approval_status": forecast_doc.approval_status,
                "approved_by": forecast_doc.approved_by,
                "approval_date": forecast_doc.approval_date,
                "approval_comments": forecast_doc.approval_comments
            },
            "metric": {
                "name": metric_doc.name,
                "metric_name": metric_doc.metric_name,
                "metric_type": metric_doc.metric_type,
                "unit_of_measure": metric_doc.unit_of_measure,
                "is_percentage": metric_doc.is_percentage,
                "is_currency": metric_doc.is_currency,
                "currency": metric_doc.currency if metric_doc.is_currency else None
            },
            "forecast_data": forecast_data,
            "performance_metrics": performance_metrics
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_forecast_data: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def generate_forecast(forecast):
    """Generate a forecast"""
    try:
        if not frappe.db.exists("Forecast", forecast):
            return {
                "status": "error",
                "message": f"Forecast {forecast} does not exist"
            }
            
        forecast_doc = frappe.get_doc("Forecast", forecast)
        
        # Check if forecast is in draft status
        if forecast_doc.status != "Draft":
            return {
                "status": "error",
                "message": f"Forecast must be in Draft status to generate"
            }
        
        # Schedule forecast generation
        forecast_doc.schedule_forecast_generation()
        
        return {
            "status": "success",
            "message": f"Forecast generation scheduled for {forecast_doc.forecast_name}",
            "forecast": forecast_doc.name
        }
        
    except Exception as e:
        frappe.log_error(f"Error in generate_forecast: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def approve_forecast(forecast, comments=None):
    """Approve a forecast"""
    try:
        if not frappe.db.exists("Forecast", forecast):
            return {
                "status": "error",
                "message": f"Forecast {forecast} does not exist"
            }
            
        forecast_doc = frappe.get_doc("Forecast", forecast)
        
        # Check if forecast is in completed status
        if forecast_doc.status != "Completed":
            return {
                "status": "error",
                "message": f"Forecast must be in Completed status to approve"
            }
        
        # Approve forecast
        forecast_doc.approve(comments)
        
        return {
            "status": "success",
            "message": f"Forecast {forecast_doc.forecast_name} approved",
            "forecast": forecast_doc.name,
            "approved_by": forecast_doc.approved_by,
            "approval_date": forecast_doc.approval_date
        }
        
    except Exception as e:
        frappe.log_error(f"Error in approve_forecast: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def reject_forecast(forecast, comments=None):
    """Reject a forecast"""
    try:
        if not frappe.db.exists("Forecast", forecast):
            return {
                "status": "error",
                "message": f"Forecast {forecast} does not exist"
            }
            
        forecast_doc = frappe.get_doc("Forecast", forecast)
        
        # Check if forecast is in completed status
        if forecast_doc.status != "Completed":
            return {
                "status": "error",
                "message": f"Forecast must be in Completed status to reject"
            }
        
        # Reject forecast
        forecast_doc.reject(comments)
        
        return {
            "status": "success",
            "message": f"Forecast {forecast_doc.forecast_name} rejected",
            "forecast": forecast_doc.name,
            "rejected_by": forecast_doc.approved_by,
            "rejection_date": forecast_doc.approval_date,
            "rejection_comments": forecast_doc.approval_comments
        }
        
    except Exception as e:
        frappe.log_error(f"Error in reject_forecast: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_data_sources(filters=None):
    """Get data sources based on filters"""
    try:
        if filters and isinstance(filters, str):
            filters = json.loads(filters)
            
        # Build query conditions
        conditions = "1=1"
        if filters:
            if filters.get("source_type"):
                conditions += f" AND source_type = '{filters['source_type']}'"
            if filters.get("is_active") is not None:
                is_active = 1 if filters["is_active"] else 0
                conditions += f" AND is_active = {is_active}"
            if filters.get("owner_user"):
                conditions += f" AND owner_user = '{filters['owner_user']}'"
            if filters.get("search"):
                conditions += f" AND (source_name LIKE '%{filters['search']}%' OR description LIKE '%{filters['search']}%')"
        
        # Execute query
        data_sources = frappe.db.sql(f"""
            SELECT name, source_name, source_type, description, 
                   connection_type, is_active, owner_user, last_refresh
            FROM `tabDataSource`
            WHERE {conditions}
            ORDER BY modified DESC
        """, as_dict=True)
        
        return {
            "status": "success",
            "data_sources": data_sources,
            "count": len(data_sources)
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_data_sources: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def test_data_source_connection(data_source):
    """Test connection to a data source"""
    try:
        if not frappe.db.exists("DataSource", data_source):
            return {
                "status": "error",
                "message": f"Data source {data_source} does not exist"
            }
            
        data_source_doc = frappe.get_doc("DataSource", data_source)
        
        # Test connection
        result = data_source_doc.test_connection()
        
        return {
            "status": "success" if result["success"] else "error",
            "message": result["message"],
            "data_source": {
                "name": data_source_doc.name,
                "source_name": data_source_doc.source_name,
                "source_type": data_source_doc.source_type
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in test_data_source_connection: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def fetch_data_source_sample(data_source):
    """Fetch sample data from a data source"""
    try:
        if not frappe.db.exists("DataSource", data_source):
            return {
                "status": "error",
                "message": f"Data source {data_source} does not exist"
            }
            
        data_source_doc = frappe.get_doc("DataSource", data_source)
        
        # Fetch sample data
        result = data_source_doc.fetch_sample_data()
        
        return {
            "status": "success" if result["success"] else "error",
            "message": result.get("message", "Sample data fetched successfully"),
            "data": result.get("data"),
            "data_source": {
                "name": data_source_doc.name,
                "source_name": data_source_doc.source_name,
                "source_type": data_source_doc.source_type
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in fetch_data_source_sample: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }"""
Main API controller for Synapse module
"""

import frappe
from frappe import _
import json
from datetime import datetime, timedelta

@frappe.whitelist()
def get_status():
    """Get the status of the Synapse module"""
    return {
        "status": "success",
        "message": _("Synapse module is active"),
        "module": "cauldron_synapse",
        "version": frappe.get_module("cauldron_synapse").__version__
    }

@frappe.whitelist()
def get_metrics(filters=None):
    """Get analytics metrics based on filters"""
    try:
        if filters and isinstance(filters, str):
            filters = json.loads(filters)
            
        # Build query conditions
        conditions = "1=1"
        if filters:
            if filters.get("metric_type"):
                conditions += f" AND metric_type = '{filters['metric_type']}'"
            if filters.get("is_active") is not None:
                is_active = 1 if filters["is_active"] else 0
                conditions += f" AND is_active = {is_active}"
            if filters.get("owner_user"):
                conditions += f" AND owner_user = '{filters['owner_user']}'"
            if filters.get("search"):
                conditions += f" AND (metric_name LIKE '%{filters['search']}%' OR description LIKE '%{filters['search']}%')"
        
        # Execute query
        metrics = frappe.db.sql(f"""
            SELECT name, metric_name, metric_type, description, business_domain, 
                   is_active, owner_user, created_date, modified_date
            FROM `tabAnalyticsMetric`
            WHERE {conditions}
            ORDER BY modified_date DESC
        """, as_dict=True)
        
        return {
            "status": "success",
            "metrics": metrics,
            "count": len(metrics)
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_metrics: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_metric_value(metric, filters=None, time_range=None):
    """Get the current value of a metric"""
    try:
        if not frappe.db.exists("AnalyticsMetric", metric):
            return {
                "status": "error",
                "message": f"Metric {metric} does not exist"
            }
            
        metric_doc = frappe.get_doc("AnalyticsMetric", metric)
        
        # Parse filters if provided
        if filters and isinstance(filters, str):
            filters = json.loads(filters)
            
        # Parse time range if provided
        if time_range and isinstance(time_range, str):
            time_range = json.loads(time_range)
        
        # Calculate metric value
        value = metric_doc.calculate_value(filters)
        
        # Check thresholds
        threshold_status = metric_doc.check_thresholds(value)
        
        return {
            "status": "success",
            "metric": {
                "name": metric_doc.name,
                "metric_name": metric_doc.metric_name,
                "metric_type": metric_doc.metric_type,
                "description": metric_doc.description
            },
            "value": value,
            "threshold_status": threshold_status["status"],
            "target": metric_doc.target_value,
            "unit": metric_doc.unit_of_measure,
            "is_percentage": metric_doc.is_percentage,
            "is_currency": metric_doc.is_currency,
            "currency": metric_doc.currency if metric_doc.is_currency else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_metric_value: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_metric_history(metric, start_date=None, end_date=None, granularity="daily"):
    """Get historical values for a metric"""
    try:
        if not frappe.db.exists("AnalyticsMetric", metric):
            return {
                "status": "error",
                "message": f"Metric {metric} does not exist"
            }
            
        metric_doc = frappe.get_doc("AnalyticsMetric", metric)
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().date()
        elif isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            
        if not start_date:
            start_date = end_date - timedelta(days=30)
        elif isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        
        # Get historical values
        history = metric_doc.get_historical_values(start_date, end_date, granularity)
        
        return {
            "status": "success",
            "metric": {
                "name": metric_doc.name,
                "metric_name": metric_doc.metric_name,
                "metric_type": metric_doc.metric_type
            },
            "history": history,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "granularity": granularity
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_metric_history: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_forecasts(filters=None):
    """Get forecasts based on filters"""
    try:
        if filters and isinstance(filters, str):
            filters = json.loads(filters)
            
        # Build query conditions
        conditions = "1=1"
        if filters:
            if filters.get("metric"):
                conditions += f" AND metric = '{filters['metric']}'"
            if filters.get("status"):
                conditions += f" AND status = '{filters['status']}'"
            if filters.get("is_active") is not None:
                is_active = 1 if filters["is_active"] else 0
                conditions += f" AND is_active = {is_active}"
            if filters.get("created_by"):
                conditions += f" AND created_by = '{filters['created_by']}'"
            if filters.get("search"):
                conditions += f" AND (forecast_name LIKE '%{filters['search']}%' OR description LIKE '%{filters['search']}%')"
        
        # Execute query
        forecasts = frappe.db.sql(f"""
            SELECT name, forecast_name, metric, status, forecast_model, 
                   forecast_horizon, forecast_frequency, is_active, 
                   created_by, creation_date, modified_date, approval_status
            FROM `tabForecast`
            WHERE {conditions}
            ORDER BY modified_date DESC
        """, as_dict=True)
        
        return {
            "status": "success",
            "forecasts": forecasts,
            "count": len(forecasts)
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_forecasts: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_forecast_data(forecast):
    """Get detailed forecast data"""
    try:
        if not frappe.db.exists("Forecast", forecast):
            return {
                "status": "error",
                "message": f"Forecast {forecast} does not exist"
            }
            
        forecast_doc = frappe.get_doc("Forecast", forecast)
        
        # Get forecast data
        forecast_data = forecast_doc.get_forecast_data()
        
        # Get performance metrics
        performance_metrics = None
        if forecast_doc.performance_metrics:
            try:
                performance_metrics = json.loads(forecast_doc.performance_metrics)
            except json.JSONDecodeError:
                performance_metrics = None
        
        # Get metric details
        metric_doc = frappe.get_doc("AnalyticsMetric", forecast_doc.metric)
        
        return {
            "status": "success",
            "forecast": {
                "name": forecast_doc.name,
                "forecast_name": forecast_doc.forecast_name,
                "description": forecast_doc.description,
                "status": forecast_doc.status,
                "forecast_model": forecast_doc.forecast_model,
                "forecast_horizon": forecast_doc.forecast_horizon,
                "forecast_frequency": forecast_doc.forecast_frequency,
                "confidence_level": forecast_doc.confidence_level,
                "forecast_date": forecast_doc.forecast_date,
                "last_historical_date": forecast_doc.last_historical_date,
                "approval_status": forecast_doc.approval_status,
                "approved_by": forecast_doc.approved_by,
                "approval_date": forecast_doc.approval_date,
                "approval_comments": forecast_doc.approval_comments
            },
            "metric": {
                "name": metric_doc.name,
                "metric_name": metric_doc.metric_name,
                "metric_type": metric_doc.metric_type,
                "unit_of_measure": metric_doc.unit_of_measure,
                "is_percentage": metric_doc.is_percentage,
                "is_currency": metric_doc.is_currency,
                "currency": metric_doc.currency if metric_doc.is_currency else None
            },
            "forecast_data": forecast_data,
            "performance_metrics": performance_metrics
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_forecast_data: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def generate_forecast(forecast):
    """Generate a forecast"""
    try:
        if not frappe.db.exists("Forecast", forecast):
            return {
                "status": "error",
                "message": f"Forecast {forecast} does not exist"
            }
            
        forecast_doc = frappe.get_doc("Forecast", forecast)
        
        # Check if forecast is in draft status
        if forecast_doc.status != "Draft":
            return {
                "status": "error",
                "message": f"Forecast must be in Draft status to generate"
            }
        
        # Schedule forecast generation
        forecast_doc.schedule_forecast_generation()
        
        return {
            "status": "success",
            "message": f"Forecast generation scheduled for {forecast_doc.forecast_name}",
            "forecast": forecast_doc.name
        }
        
    except Exception as e:
        frappe.log_error(f"Error in generate_forecast: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def approve_forecast(forecast, comments=None):
    """Approve a forecast"""
    try:
        if not frappe.db.exists("Forecast", forecast):
            return {
                "status": "error",
                "message": f"Forecast {forecast} does not exist"
            }
            
        forecast_doc = frappe.get_doc("Forecast", forecast)
        
        # Check if forecast is in completed status
        if forecast_doc.status != "Completed":
            return {
                "status": "error",
                "message": f"Forecast must be in Completed status to approve"
            }
        
        # Approve forecast
        forecast_doc.approve(comments)
        
        return {
            "status": "success",
            "message": f"Forecast {forecast_doc.forecast_name} approved",
            "forecast": forecast_doc.name,
            "approved_by": forecast_doc.approved_by,
            "approval_date": forecast_doc.approval_date
        }
        
    except Exception as e:
        frappe.log_error(f"Error in approve_forecast: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def reject_forecast(forecast, comments=None):
    """Reject a forecast"""
    try:
        if not frappe.db.exists("Forecast", forecast):
            return {
                "status": "error",
                "message": f"Forecast {forecast} does not exist"
            }
            
        forecast_doc = frappe.get_doc("Forecast", forecast)
        
        # Check if forecast is in completed status
        if forecast_doc.status != "Completed":
            return {
                "status": "error",
                "message": f"Forecast must be in Completed status to reject"
            }
        
        # Reject forecast
        forecast_doc.reject(comments)
        
        return {
            "status": "success",
            "message": f"Forecast {forecast_doc.forecast_name} rejected",
            "forecast": forecast_doc.name,
            "rejected_by": forecast_doc.approved_by,
            "rejection_date": forecast_doc.approval_date,
            "rejection_comments": forecast_doc.approval_comments
        }
        
    except Exception as e:
        frappe.log_error(f"Error in reject_forecast: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_data_sources(filters=None):
    """Get data sources based on filters"""
    try:
        if filters and isinstance(filters, str):
            filters = json.loads(filters)
            
        # Build query conditions
        conditions = "1=1"
        if filters:
            if filters.get("source_type"):
                conditions += f" AND source_type = '{filters['source_type']}'"
            if filters.get("is_active") is not None:
                is_active = 1 if filters["is_active"] else 0
                conditions += f" AND is_active = {is_active}"
            if filters.get("owner_user"):
                conditions += f" AND owner_user = '{filters['owner_user']}'"
            if filters.get("search"):
                conditions += f" AND (source_name LIKE '%{filters['search']}%' OR description LIKE '%{filters['search']}%')"
        
        # Execute query
        data_sources = frappe.db.sql(f"""
            SELECT name, source_name, source_type, description, 
                   connection_type, is_active, owner_user, last_refresh
            FROM `tabDataSource`
            WHERE {conditions}
            ORDER BY modified DESC
        """, as_dict=True)
        
        return {
            "status": "success",
            "data_sources": data_sources,
            "count": len(data_sources)
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_data_sources: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def test_data_source_connection(data_source):
    """Test connection to a data source"""
    try:
        if not frappe.db.exists("DataSource", data_source):
            return {
                "status": "error",
                "message": f"Data source {data_source} does not exist"
            }
            
        data_source_doc = frappe.get_doc("DataSource", data_source)
        
        # Test connection
        result = data_source_doc.test_connection()
        
        return {
            "status": "success" if result["success"] else "error",
            "message": result["message"],
            "data_source": {
                "name": data_source_doc.name,
                "source_name": data_source_doc.source_name,
                "source_type": data_source_doc.source_type
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in test_data_source_connection: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def fetch_data_source_sample(data_source):
    """Fetch sample data from a data source"""
    try:
        if not frappe.db.exists("DataSource", data_source):
            return {
                "status": "error",
                "message": f"Data source {data_source} does not exist"
            }
            
        data_source_doc = frappe.get_doc("DataSource", data_source)
        
        # Fetch sample data
        result = data_source_doc.fetch_sample_data()
        
        return {
            "status": "success" if result["success"] else "error",
            "message": result.get("message", "Sample data fetched successfully"),
            "data": result.get("data"),
            "data_source": {
                "name": data_source_doc.name,
                "source_name": data_source_doc.source_name,
                "source_type": data_source_doc.source_type
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in fetch_data_source_sample: {str(e)}", "API Error")
        return {
            "status": "error",
            "message": str(e)
        }