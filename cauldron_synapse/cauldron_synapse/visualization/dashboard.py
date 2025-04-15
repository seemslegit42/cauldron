"""
Dashboard module for the Visualization layer
"""

import frappe
import json
from datetime import datetime, timedelta
import logging

# Configure logger
logger = logging.getLogger(__name__)

def get_dashboard_data(dashboard_id):
    """Get data for a dashboard"""
    try:
        dashboard_doc = frappe.get_doc("Dashboard", dashboard_id)
        
        logger.info(f"Getting data for dashboard: {dashboard_doc.dashboard_name}")
        
        # Get dashboard components
        components = frappe.get_all(
            "Dashboard Component",
            filters={"dashboard": dashboard_id, "is_active": 1},
            fields=["name", "component_type", "title", "metric", "chart_type", 
                    "time_range", "refresh_frequency", "size", "position"]
        )
        
        # Get data for each component
        component_data = []
        for component in components:
            data = get_component_data(component)
            component_data.append({
                "component_id": component.name,
                "component_type": component.component_type,
                "title": component.title,
                "metric": component.metric,
                "chart_type": component.chart_type,
                "size": component.size,
                "position": component.position,
                "data": data
            })
        
        # Update last viewed timestamp
        dashboard_doc.last_viewed = datetime.now()
        dashboard_doc.save()
        
        return {
            "success": True,
            "dashboard_id": dashboard_id,
            "dashboard_name": dashboard_doc.dashboard_name,
            "description": dashboard_doc.description,
            "components": component_data,
            "last_refresh": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        frappe.log_error(f"Error getting dashboard data: {str(e)}", "Dashboard Error")
        return {
            "success": False,
            "error": str(e)
        }

def get_component_data(component):
    """Get data for a dashboard component"""
    try:
        if component.component_type == "Metric":
            return get_metric_component_data(component)
        elif component.component_type == "Chart":
            return get_chart_component_data(component)
        elif component.component_type == "Table":
            return get_table_component_data(component)
        elif component.component_type == "Forecast":
            return get_forecast_component_data(component)
        elif component.component_type == "Anomaly":
            return get_anomaly_component_data(component)
        elif component.component_type == "Recommendation":
            return get_recommendation_component_data(component)
        else:
            return {
                "error": f"Unsupported component type: {component.component_type}"
            }
        
    except Exception as e:
        logger.error(f"Error getting component data: {str(e)}")
        frappe.log_error(f"Error getting component data: {str(e)}", "Component Error")
        return {
            "error": str(e)
        }

def get_metric_component_data(component):
    """Get data for a metric component"""
    try:
        metric_doc = frappe.get_doc("AnalyticsMetric", component.metric)
        
        # Calculate current value
        current_value = metric_doc.calculate_value()
        
        # Check thresholds
        threshold_status = metric_doc.check_thresholds(current_value)
        
        # Get previous value for comparison
        previous_value = get_previous_value(metric_doc)
        
        # Calculate change
        change = None
        change_percent = None
        if previous_value is not None and previous_value != 0:
            change = current_value - previous_value
            change_percent = (change / previous_value) * 100
        
        return {
            "current_value": current_value,
            "formatted_value": format_value(current_value, metric_doc),
            "previous_value": previous_value,
            "formatted_previous_value": format_value(previous_value, metric_doc) if previous_value is not None else None,
            "change": change,
            "change_percent": change_percent,
            "trend": "up" if change_percent and change_percent > 0 else "down" if change_percent and change_percent < 0 else "flat",
            "status": threshold_status["status"],
            "target": metric_doc.target_value,
            "unit": metric_doc.unit_of_measure,
            "is_percentage": metric_doc.is_percentage,
            "is_currency": metric_doc.is_currency,
            "currency": metric_doc.currency if metric_doc.is_currency else None
        }
        
    except Exception as e:
        logger.error(f"Error getting metric component data: {str(e)}")
        frappe.log_error(f"Error getting metric component data: {str(e)}", "Metric Component Error")
        return {
            "error": str(e)
        }

def get_chart_component_data(component):
    """Get data for a chart component"""
    try:
        metric_doc = frappe.get_doc("AnalyticsMetric", component.metric)
        
        # Parse time range
        time_range = component.time_range or "30d"
        end_date = datetime.now().date()
        
        if time_range == "7d":
            start_date = end_date - timedelta(days=7)
        elif time_range == "30d":
            start_date = end_date - timedelta(days=30)
        elif time_range == "90d":
            start_date = end_date - timedelta(days=90)
        elif time_range == "1y":
            start_date = end_date - timedelta(days=365)
        elif time_range == "ytd":
            start_date = datetime(end_date.year, 1, 1).date()
        else:
            # Default to 30 days
            start_date = end_date - timedelta(days=30)
        
        # Get historical data
        historical_data = metric_doc.get_historical_values(start_date, end_date)
        
        # Get forecast data if available
        forecast_data = get_forecast_data(metric_doc, end_date)
        
        # Format data for chart
        chart_data = {
            "labels": [point["date"] for point in historical_data],
            "datasets": [
                {
                    "label": "Actual",
                    "data": [point["value"] for point in historical_data],
                    "borderColor": "#4285F4",
                    "backgroundColor": "rgba(66, 133, 244, 0.2)"
                }
            ]
        }
        
        # Add forecast dataset if available
        if forecast_data:
            chart_data["datasets"].append({
                "label": "Forecast",
                "data": [None] * len(historical_data) + [point["value"] for point in forecast_data],
                "borderColor": "#34A853",
                "backgroundColor": "rgba(52, 168, 83, 0.2)",
                "borderDash": [5, 5]
            })
            
            # Add forecast labels
            chart_data["labels"].extend([point["date"] for point in forecast_data])
            
            # Add confidence intervals if available
            if "lower_bound" in forecast_data[0] and "upper_bound" in forecast_data[0]:
                lower_bounds = [None] * len(historical_data) + [point["lower_bound"] for point in forecast_data]
                upper_bounds = [None] * len(historical_data) + [point["upper_bound"] for point in forecast_data]
                
                chart_data["datasets"].append({
                    "label": "Confidence Interval",
                    "data": lower_bounds,
                    "borderColor": "rgba(52, 168, 83, 0.3)",
                    "backgroundColor": "rgba(52, 168, 83, 0.1)",
                    "borderDash": [2, 2],
                    "fill": "+1"
                })
                
                chart_data["datasets"].append({
                    "label": "Confidence Interval",
                    "data": upper_bounds,
                    "borderColor": "rgba(52, 168, 83, 0.3)",
                    "backgroundColor": "rgba(52, 168, 83, 0.1)",
                    "borderDash": [2, 2],
                    "fill": "-1"
                })
        
        # Add anomalies if available
        anomalies = get_anomalies(metric_doc, start_date, end_date)
        if anomalies:
            # Create a sparse dataset with nulls except at anomaly points
            anomaly_data = [None] * len(historical_data)
            for anomaly in anomalies:
                # Find the index of the anomaly date in the labels
                try:
                    index = chart_data["labels"].index(anomaly["anomaly_date"])
                    anomaly_data[index] = historical_data[index]["value"]
                except ValueError:
                    # Date not found in labels
                    pass
            
            chart_data["datasets"].append({
                "label": "Anomalies",
                "data": anomaly_data,
                "borderColor": "#EA4335",
                "backgroundColor": "#EA4335",
                "pointRadius": 6,
                "pointHoverRadius": 8,
                "showLine": False
            })
        
        return {
            "chart_type": component.chart_type,
            "chart_data": chart_data,
            "unit": metric_doc.unit_of_measure,
            "is_percentage": metric_doc.is_percentage,
            "is_currency": metric_doc.is_currency,
            "currency": metric_doc.currency if metric_doc.is_currency else None,
            "time_range": time_range,
            "has_forecast": bool(forecast_data),
            "has_anomalies": bool(anomalies)
        }
        
    except Exception as e:
        logger.error(f"Error getting chart component data: {str(e)}")
        frappe.log_error(f"Error getting chart component data: {str(e)}", "Chart Component Error")
        return {
            "error": str(e)
        }

def get_table_component_data(component):
    """Get data for a table component"""
    try:
        metric_doc = frappe.get_doc("AnalyticsMetric", component.metric)
        
        # Parse time range
        time_range = component.time_range or "30d"
        end_date = datetime.now().date()
        
        if time_range == "7d":
            start_date = end_date - timedelta(days=7)
        elif time_range == "30d":
            start_date = end_date - timedelta(days=30)
        elif time_range == "90d":
            start_date = end_date - timedelta(days=90)
        elif time_range == "1y":
            start_date = end_date - timedelta(days=365)
        elif time_range == "ytd":
            start_date = datetime(end_date.year, 1, 1).date()
        else:
            # Default to 30 days
            start_date = end_date - timedelta(days=30)
        
        # Get historical data
        historical_data = metric_doc.get_historical_values(start_date, end_date)
        
        # Format data for table
        table_data = []
        for point in historical_data:
            table_data.append({
                "date": point["date"],
                "value": point["value"],
                "formatted_value": format_value(point["value"], metric_doc)
            })
        
        return {
            "columns": [
                {"field": "date", "title": "Date"},
                {"field": "formatted_value", "title": metric_doc.metric_name}
            ],
            "data": table_data,
            "unit": metric_doc.unit_of_measure,
            "is_percentage": metric_doc.is_percentage,
            "is_currency": metric_doc.is_currency,
            "currency": metric_doc.currency if metric_doc.is_currency else None,
            "time_range": time_range
        }
        
    except Exception as e:
        logger.error(f"Error getting table component data: {str(e)}")
        frappe.log_error(f"Error getting table component data: {str(e)}", "Table Component Error")
        return {
            "error": str(e)
        }

def get_forecast_component_data(component):
    """Get data for a forecast component"""
    try:
        metric_doc = frappe.get_doc("AnalyticsMetric", component.metric)
        
        # Get latest forecast
        forecasts = frappe.get_all(
            "Forecast",
            filters={
                "metric": component.metric,
                "status": "Completed",
                "is_active": 1
            },
            fields=["name", "forecast_name", "forecast_model", "forecast_date", "forecast_horizon"],
            order_by="forecast_date DESC",
            limit=1
        )
        
        if not forecasts:
            return {
                "error": "No forecasts available"
            }
        
        forecast_doc = frappe.get_doc("Forecast", forecasts[0].name)
        
        # Get forecast data
        forecast_data = forecast_doc.get_forecast_data()
        
        if not forecast_data:
            return {
                "error": "Forecast data not available"
            }
        
        # Get performance metrics
        performance_metrics = None
        if forecast_doc.performance_metrics:
            try:
                performance_metrics = json.loads(forecast_doc.performance_metrics)
            except json.JSONDecodeError:
                performance_metrics = None
        
        # Calculate summary statistics
        first_value = forecast_data[0]["value"]
        last_value = forecast_data[-1]["value"]
        percent_change = ((last_value - first_value) / first_value) * 100 if first_value != 0 else 0
        trend = "up" if percent_change > 0 else "down" if percent_change < 0 else "flat"
        
        # Format data for chart
        chart_data = {
            "labels": [point["date"] for point in forecast_data],
            "datasets": [
                {
                    "label": "Forecast",
                    "data": [point["value"] for point in forecast_data],
                    "borderColor": "#34A853",
                    "backgroundColor": "rgba(52, 168, 83, 0.2)"
                }
            ]
        }
        
        # Add confidence intervals if available
        if "lower_bound" in forecast_data[0] and "upper_bound" in forecast_data[0]:
            lower_bounds = [point["lower_bound"] for point in forecast_data]
            upper_bounds = [point["upper_bound"] for point in forecast_data]
            
            chart_data["datasets"].append({
                "label": "Lower Bound",
                "data": lower_bounds,
                "borderColor": "rgba(52, 168, 83, 0.3)",
                "backgroundColor": "rgba(52, 168, 83, 0.1)",
                "borderDash": [2, 2],
                "fill": "+1"
            })
            
            chart_data["datasets"].append({
                "label": "Upper Bound",
                "data": upper_bounds,
                "borderColor": "rgba(52, 168, 83, 0.3)",
                "backgroundColor": "rgba(52, 168, 83, 0.1)",
                "borderDash": [2, 2],
                "fill": "-1"
            })
        
        return {
            "forecast_id": forecast_doc.name,
            "forecast_name": forecast_doc.forecast_name,
            "forecast_model": forecast_doc.forecast_model,
            "forecast_date": forecast_doc.forecast_date,
            "forecast_horizon": forecast_doc.forecast_horizon,
            "chart_data": chart_data,
            "summary": {
                "first_value": first_value,
                "last_value": last_value,
                "percent_change": percent_change,
                "trend": trend
            },
            "performance_metrics": performance_metrics,
            "unit": metric_doc.unit_of_measure,
            "is_percentage": metric_doc.is_percentage,
            "is_currency": metric_doc.is_currency,
            "currency": metric_doc.currency if metric_doc.is_currency else None
        }
        
    except Exception as e:
        logger.error(f"Error getting forecast component data: {str(e)}")
        frappe.log_error(f"Error getting forecast component data: {str(e)}", "Forecast Component Error")
        return {
            "error": str(e)
        }

def get_anomaly_component_data(component):
    """Get data for an anomaly component"""
    try:
        metric_doc = frappe.get_doc("AnalyticsMetric", component.metric)
        
        # Parse time range
        time_range = component.time_range or "30d"
        end_date = datetime.now().date()
        
        if time_range == "7d":
            start_date = end_date - timedelta(days=7)
        elif time_range == "30d":
            start_date = end_date - timedelta(days=30)
        elif time_range == "90d":
            start_date = end_date - timedelta(days=90)
        elif time_range == "1y":
            start_date = end_date - timedelta(days=365)
        elif time_range == "ytd":
            start_date = datetime(end_date.year, 1, 1).date()
        else:
            # Default to 30 days
            start_date = end_date - timedelta(days=30)
        
        # Get anomalies
        anomalies = frappe.get_all(
            "Anomaly",
            filters={
                "metric": component.metric,
                "anomaly_date": ["between", [start_date, end_date]],
                "status": ["!=", "Archived"]
            },
            fields=["name", "anomaly_date", "value", "expected_value", "deviation", 
                    "severity", "detection_method", "status", "description"],
            order_by="anomaly_date DESC"
        )
        
        # Format anomalies for display
        formatted_anomalies = []
        for anomaly in anomalies:
            formatted_anomalies.append({
                "anomaly_id": anomaly.name,
                "date": anomaly.anomaly_date,
                "value": anomaly.value,
                "formatted_value": format_value(anomaly.value, metric_doc),
                "expected_value": anomaly.expected_value,
                "formatted_expected_value": format_value(anomaly.expected_value, metric_doc),
                "deviation": anomaly.deviation,
                "percent_deviation": ((anomaly.value - anomaly.expected_value) / anomaly.expected_value) * 100 if anomaly.expected_value != 0 else 0,
                "severity": anomaly.severity,
                "detection_method": anomaly.detection_method,
                "status": anomaly.status,
                "description": anomaly.description
            })
        
        return {
            "anomalies": formatted_anomalies,
            "count": len(formatted_anomalies),
            "time_range": time_range,
            "unit": metric_doc.unit_of_measure,
            "is_percentage": metric_doc.is_percentage,
            "is_currency": metric_doc.is_currency,
            "currency": metric_doc.currency if metric_doc.is_currency else None
        }
        
    except Exception as e:
        logger.error(f"Error getting anomaly component data: {str(e)}")
        frappe.log_error(f"Error getting anomaly component data: {str(e)}", "Anomaly Component Error")
        return {
            "error": str(e)
        }

def get_recommendation_component_data(component):
    """Get data for a recommendation component"""
    try:
        # Get recommendations
        recommendations = frappe.get_all(
            "Recommendation",
            filters={
                "metric": component.metric,
                "status": ["in", ["New", "In Progress"]]
            },
            fields=["name", "title", "description", "recommendation_type", 
                    "priority", "source", "creation_date", "status"],
            order_by="creation_date DESC",
            limit=5
        )
        
        # Format recommendations for display
        formatted_recommendations = []
        for recommendation in recommendations:
            formatted_recommendations.append({
                "recommendation_id": recommendation.name,
                "title": recommendation.title,
                "description": recommendation.description,
                "type": recommendation.recommendation_type,
                "priority": recommendation.priority,
                "source": recommendation.source,
                "creation_date": recommendation.creation_date,
                "status": recommendation.status
            })
        
        return {
            "recommendations": formatted_recommendations,
            "count": len(formatted_recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendation component data: {str(e)}")
        frappe.log_error(f"Error getting recommendation component data: {str(e)}", "Recommendation Component Error")
        return {
            "error": str(e)
        }

def get_previous_value(metric_doc):
    """Get previous value for a metric"""
    try:
        # This would be implemented to get the actual previous value
        # For now, return a placeholder value
        current_value = metric_doc.calculate_value()
        return current_value * 0.9  # Placeholder: 90% of current value
        
    except Exception as e:
        logger.error(f"Error getting previous value: {str(e)}")
        frappe.log_error(f"Error getting previous value: {str(e)}", "Previous Value Error")
        return None

def get_forecast_data(metric_doc, end_date):
    """Get forecast data for a metric"""
    try:
        # Get latest forecast
        forecasts = frappe.get_all(
            "Forecast",
            filters={
                "metric": metric_doc.name,
                "status": "Completed",
                "is_active": 1
            },
            fields=["name"],
            order_by="forecast_date DESC",
            limit=1
        )
        
        if not forecasts:
            return None
        
        forecast_doc = frappe.get_doc("Forecast", forecasts[0].name)
        
        # Get forecast data
        forecast_data = forecast_doc.get_forecast_data()
        
        return forecast_data
        
    except Exception as e:
        logger.error(f"Error getting forecast data: {str(e)}")
        frappe.log_error(f"Error getting forecast data: {str(e)}", "Forecast Data Error")
        return None

def get_anomalies(metric_doc, start_date, end_date):
    """Get anomalies for a metric"""
    try:
        # Get anomalies
        anomalies = frappe.get_all(
            "Anomaly",
            filters={
                "metric": metric_doc.name,
                "anomaly_date": ["between", [start_date, end_date]],
                "status": ["!=", "Archived"]
            },
            fields=["name", "anomaly_date", "value", "expected_value", "deviation", "severity"],
            order_by="anomaly_date"
        )
        
        return anomalies
        
    except Exception as e:
        logger.error(f"Error getting anomalies: {str(e)}")
        frappe.log_error(f"Error getting anomalies: {str(e)}", "Anomalies Error")
        return None

def format_value(value, metric_doc):
    """Format a value based on metric settings"""
    try:
        if value is None:
            return None
            
        # Apply decimal places
        if metric_doc.decimal_places is not None:
            formatted_value = round(value, metric_doc.decimal_places)
        else:
            formatted_value = value
        
        # Apply format string if specified
        if metric_doc.format_string:
            return metric_doc.format_string.format(formatted_value)
        
        # Apply currency formatting
        if metric_doc.is_currency:
            return f"{metric_doc.currency} {formatted_value:,.2f}"
        
        # Apply percentage formatting
        if metric_doc.is_percentage:
            return f"{formatted_value:,.2f}%"
        
        # Apply unit of measure
        if metric_doc.unit_of_measure:
            return f"{formatted_value:,} {metric_doc.unit_of_measure}"
        
        # Default formatting
        return f"{formatted_value:,}"
        
    except Exception as e:
        logger.error(f"Error formatting value: {str(e)}")
        frappe.log_error(f"Error formatting value: {str(e)}", "Formatting Error")
        return str(value)