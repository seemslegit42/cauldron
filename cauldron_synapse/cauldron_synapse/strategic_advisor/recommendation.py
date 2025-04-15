"""
Recommendation module for the Strategic Advisor layer
"""

import frappe
import json
from datetime import datetime, timedelta
import random

def generate_recommendations():
    """Generate recommendations based on insights, forecasts, and anomalies"""
    try:
        frappe.logger().info("Generating recommendations")
        
        # Get recent forecasts
        recent_forecasts = get_recent_forecasts()
        
        # Get recent anomalies
        recent_anomalies = get_recent_anomalies()
        
        # Generate recommendations from forecasts
        forecast_recommendations = generate_forecast_recommendations(recent_forecasts)
        
        # Generate recommendations from anomalies
        anomaly_recommendations = generate_anomaly_recommendations(recent_anomalies)
        
        # Combine and prioritize recommendations
        all_recommendations = forecast_recommendations + anomaly_recommendations
        prioritized_recommendations = prioritize_recommendations(all_recommendations)
        
        # Store recommendations
        stored_recommendations = store_recommendations(prioritized_recommendations)
        
        # Publish recommendation events
        publish_recommendation_events(stored_recommendations)
        
        return {
            "success": True,
            "recommendations_generated": len(stored_recommendations),
            "recommendations": stored_recommendations
        }
        
    except Exception as e:
        frappe.log_error(f"Error generating recommendations: {str(e)}", "Recommendation Error")
        return {
            "success": False,
            "error": str(e)
        }

def get_recent_forecasts():
    """Get recent forecasts for recommendation generation"""
    try:
        # Get forecasts completed in the last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        
        forecasts = frappe.get_all(
            "Forecast",
            filters={
                "status": "Completed",
                "is_active": 1,
                "forecast_date": [">=", cutoff_date]
            },
            fields=["name", "forecast_name", "metric", "forecast_model", "forecast_date"]
        )
        
        # Fetch additional details for each forecast
        detailed_forecasts = []
        for forecast in forecasts:
            forecast_doc = frappe.get_doc("Forecast", forecast.name)
            metric_doc = frappe.get_doc("AnalyticsMetric", forecast_doc.metric)
            
            forecast_data = None
            if forecast_doc.forecast_values:
                try:
                    forecast_data = json.loads(forecast_doc.forecast_values)
                except json.JSONDecodeError:
                    forecast_data = None
            
            if forecast_data:
                detailed_forecasts.append({
                    "forecast_id": forecast_doc.name,
                    "forecast_name": forecast_doc.forecast_name,
                    "metric_id": metric_doc.name,
                    "metric_name": metric_doc.metric_name,
                    "metric_type": metric_doc.metric_type,
                    "forecast_date": forecast_doc.forecast_date,
                    "forecast_horizon": forecast_doc.forecast_horizon,
                    "forecast_data": forecast_data,
                    "first_value": forecast_data[0]["value"] if forecast_data else None,
                    "last_value": forecast_data[-1]["value"] if forecast_data else None
                })
        
        return detailed_forecasts
        
    except Exception as e:
        frappe.log_error(f"Error getting recent forecasts: {str(e)}", "Forecast Retrieval Error")
        return []

def get_recent_anomalies():
    """Get recent anomalies for recommendation generation"""
    try:
        # Get anomalies detected in the last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        
        anomalies = frappe.get_all(
            "Anomaly",
            filters={
                "detection_date": [">=", cutoff_date],
                "status": ["in", ["New", "Analyzed"]]
            },
            fields=["name", "metric", "anomaly_date", "value", "expected_value", 
                    "deviation", "severity", "detection_method", "status"]
        )
        
        # Fetch additional details for each anomaly
        detailed_anomalies = []
        for anomaly in anomalies:
            metric_doc = frappe.get_doc("AnalyticsMetric", anomaly.metric)
            
            analysis_results = None
            if hasattr(anomaly, 'analysis_results') and anomaly.analysis_results:
                try:
                    analysis_results = json.loads(anomaly.analysis_results)
                except json.JSONDecodeError:
                    analysis_results = None
            
            detailed_anomalies.append({
                "anomaly_id": anomaly.name,
                "metric_id": metric_doc.name,
                "metric_name": metric_doc.metric_name,
                "metric_type": metric_doc.metric_type,
                "anomaly_date": anomaly.anomaly_date,
                "value": anomaly.value,
                "expected_value": anomaly.expected_value,
                "deviation": anomaly.deviation,
                "severity": anomaly.severity,
                "detection_method": anomaly.detection_method,
                "status": anomaly.status,
                "analysis_results": analysis_results
            })
        
        return detailed_anomalies
        
    except Exception as e:
        frappe.log_error(f"Error getting recent anomalies: {str(e)}", "Anomaly Retrieval Error")
        return []

def generate_forecast_recommendations(forecasts):
    """Generate recommendations based on forecasts"""
    try:
        recommendations = []
        
        for forecast in forecasts:
            # Skip if missing key data
            if not forecast.get("forecast_data") or not forecast.get("first_value") or not forecast.get("last_value"):
                continue
            
            # Calculate percent change
            first_value = forecast["first_value"]
            last_value = forecast["last_value"]
            percent_change = (last_value - first_value) / first_value * 100
            
            # Generate recommendation based on trend
            if abs(percent_change) > 10:  # Significant change threshold
                trend = "increasing" if percent_change > 0 else "decreasing"
                severity = "High" if abs(percent_change) > 20 else "Medium"
                
                # Determine recommendation type based on metric type
                recommendation_type = "Opportunity" if (
                    (trend == "increasing" and forecast["metric_type"] in ["Sales Metric", "Revenue Metric", "Customer Metric"]) or
                    (trend == "decreasing" and forecast["metric_type"] in ["Cost Metric", "Expense Metric"])
                ) else "Risk"
                
                # Generate recommendation
                recommendation = {
                    "title": f"Significant {trend} trend in {forecast['metric_name']}",
                    "description": f"Forecast shows a {trend} trend of {abs(percent_change):.2f}% over the next {forecast['forecast_horizon']} periods.",
                    "recommendation_type": recommendation_type,
                    "priority": severity,
                    "source": "Forecast",
                    "source_reference": forecast["forecast_id"],
                    "metric": forecast["metric_id"],
                    "metric_name": forecast["metric_name"],
                    "impact": generate_impact_assessment(forecast, percent_change),
                    "suggested_actions": generate_suggested_actions(forecast, trend, percent_change),
                    "confidence": random.uniform(0.7, 0.95)  # Would be calculated based on forecast accuracy
                }
                
                recommendations.append(recommendation)
        
        return recommendations
        
    except Exception as e:
        frappe.log_error(f"Error generating forecast recommendations: {str(e)}", "Forecast Recommendation Error")
        return []

def generate_anomaly_recommendations(anomalies):
    """Generate recommendations based on anomalies"""
    try:
        recommendations = []
        
        for anomaly in anomalies:
            # Skip if missing key data
            if not anomaly.get("value") or not anomaly.get("expected_value"):
                continue
            
            # Calculate percent deviation
            value = anomaly["value"]
            expected_value = anomaly["expected_value"]
            percent_deviation = (value - expected_value) / expected_value * 100 if expected_value else 0
            
            # Generate recommendation based on anomaly
            direction = "above" if percent_deviation > 0 else "below"
            
            # Determine recommendation type based on metric type and direction
            recommendation_type = "Opportunity" if (
                (direction == "above" and anomaly["metric_type"] in ["Sales Metric", "Revenue Metric", "Customer Metric"]) or
                (direction == "below" and anomaly["metric_type"] in ["Cost Metric", "Expense Metric"])
            ) else "Risk"
            
            # Generate recommendation
            recommendation = {
                "title": f"Significant anomaly detected in {anomaly['metric_name']}",
                "description": f"Value of {value:.2f} is {abs(percent_deviation):.2f}% {direction} expected value of {expected_value:.2f}.",
                "recommendation_type": recommendation_type,
                "priority": anomaly["severity"],
                "source": "Anomaly",
                "source_reference": anomaly["anomaly_id"],
                "metric": anomaly["metric_id"],
                "metric_name": anomaly["metric_name"],
                "impact": generate_impact_assessment_for_anomaly(anomaly, percent_deviation),
                "suggested_actions": generate_suggested_actions_for_anomaly(anomaly, direction, percent_deviation),
                "confidence": 0.85  # Would be calculated based on anomaly detection method
            }
            
            recommendations.append(recommendation)
        
        return recommendations
        
    except Exception as e:
        frappe.log_error(f"Error generating anomaly recommendations: {str(e)}", "Anomaly Recommendation Error")
        return []

def generate_impact_assessment(forecast, percent_change):
    """Generate impact assessment for a forecast-based recommendation"""
    try:
        # This would be implemented with actual business logic
        # For now, return placeholder impact assessment
        
        impact = {
            "financial_impact": {
                "estimated_value": random.uniform(10000, 100000),
                "confidence": random.uniform(0.6, 0.9)
            },
            "operational_impact": "Medium",
            "customer_impact": "Low",
            "timeframe": "Medium-term",
            "affected_areas": ["Sales", "Inventory"]
        }
        
        return impact
        
    except Exception as e:
        frappe.log_error(f"Error generating impact assessment: {str(e)}", "Impact Assessment Error")
        return {}

def generate_suggested_actions(forecast, trend, percent_change):
    """Generate suggested actions for a forecast-based recommendation"""
    try:
        # This would be implemented with actual business logic
        # For now, return placeholder suggested actions
        
        if trend == "increasing" and forecast["metric_type"] in ["Sales Metric", "Revenue Metric"]:
            actions = [
                "Increase inventory levels to meet projected demand",
                "Review staffing levels to ensure adequate coverage",
                "Analyze which products or services are driving the growth",
                "Consider promotional activities to capitalize on positive trend"
            ]
        elif trend == "decreasing" and forecast["metric_type"] in ["Sales Metric", "Revenue Metric"]:
            actions = [
                "Investigate root causes of the declining trend",
                "Review pricing strategy and competitive positioning",
                "Develop marketing campaigns to reverse the trend",
                "Consider cost reduction measures if trend continues"
            ]
        elif trend == "increasing" and forecast["metric_type"] in ["Cost Metric", "Expense Metric"]:
            actions = [
                "Identify drivers of cost increases",
                "Review vendor contracts and consider renegotiation",
                "Implement cost control measures",
                "Evaluate process efficiency improvements"
            ]
        elif trend == "decreasing" and forecast["metric_type"] in ["Cost Metric", "Expense Metric"]:
            actions = [
                "Document cost-saving measures for replication",
                "Ensure quality and service levels are maintained",
                "Reinvest savings in growth opportunities",
                "Share best practices across the organization"
            ]
        else:
            actions = [
                "Monitor the trend closely",
                "Conduct further analysis to understand implications",
                "Develop contingency plans",
                "Review related metrics for correlation"
            ]
        
        return actions
        
    except Exception as e:
        frappe.log_error(f"Error generating suggested actions: {str(e)}", "Suggested Actions Error")
        return []

def generate_impact_assessment_for_anomaly(anomaly, percent_deviation):
    """Generate impact assessment for an anomaly-based recommendation"""
    try:
        # This would be implemented with actual business logic
        # For now, return placeholder impact assessment
        
        impact = {
            "financial_impact": {
                "estimated_value": random.uniform(5000, 50000),
                "confidence": random.uniform(0.5, 0.8)
            },
            "operational_impact": "High" if anomaly["severity"] == "High" else "Medium",
            "customer_impact": "Medium",
            "timeframe": "Immediate",
            "affected_areas": ["Operations", "Finance"]
        }
        
        return impact
        
    except Exception as e:
        frappe.log_error(f"Error generating anomaly impact assessment: {str(e)}", "Anomaly Impact Assessment Error")
        return {}

def generate_suggested_actions_for_anomaly(anomaly, direction, percent_deviation):
    """Generate suggested actions for an anomaly-based recommendation"""
    try:
        # This would be implemented with actual business logic
        # For now, return placeholder suggested actions
        
        if direction == "above" and anomaly["metric_type"] in ["Sales Metric", "Revenue Metric"]:
            actions = [
                "Verify data accuracy to confirm the spike",
                "Identify which products or services contributed to the increase",
                "Analyze marketing or sales activities that may have driven the spike",
                "Consider if this represents a new trend or a one-time event"
            ]
        elif direction == "below" and anomaly["metric_type"] in ["Sales Metric", "Revenue Metric"]:
            actions = [
                "Verify data accuracy to confirm the drop",
                "Check for system issues or data collection problems",
                "Investigate competitive actions or market changes",
                "Develop immediate response plan if confirmed"
            ]
        elif direction == "above" and anomaly["metric_type"] in ["Cost Metric", "Expense Metric"]:
            actions = [
                "Verify data accuracy to confirm the spike",
                "Identify specific cost categories contributing to the increase",
                "Check for duplicate transactions or accounting errors",
                "Implement immediate cost controls if confirmed"
            ]
        elif direction == "below" and anomaly["metric_type"] in ["Cost Metric", "Expense Metric"]:
            actions = [
                "Verify data accuracy to confirm the drop",
                "Identify which cost categories decreased",
                "Document cost-saving measures for replication",
                "Ensure service quality has not been compromised"
            ]
        else:
            actions = [
                "Investigate root causes of the anomaly",
                "Check for data quality issues",
                "Determine if this is part of a larger pattern",
                "Monitor closely for recurrence"
            ]
        
        # Add analysis-based actions if available
        if anomaly.get("analysis_results") and anomaly["analysis_results"].get("recommended_actions"):
            actions.extend(anomaly["analysis_results"]["recommended_actions"])
        
        return actions
        
    except Exception as e:
        frappe.log_error(f"Error generating anomaly suggested actions: {str(e)}", "Anomaly Suggested Actions Error")
        return []

def prioritize_recommendations(recommendations):
    """Prioritize recommendations based on impact, confidence, and relevance"""
    try:
        # This would be implemented with actual prioritization logic
        # For now, just sort by priority
        
        priority_scores = {
            "High": 3,
            "Medium": 2,
            "Low": 1
        }
        
        # Add a priority score to each recommendation
        for recommendation in recommendations:
            base_score = priority_scores.get(recommendation["priority"], 1)
            confidence_factor = recommendation.get("confidence", 0.5)
            
            # Calculate a composite score
            recommendation["priority_score"] = base_score * confidence_factor
        
        # Sort by priority score (descending)
        sorted_recommendations = sorted(
            recommendations, 
            key=lambda x: x.get("priority_score", 0), 
            reverse=True
        )
        
        return sorted_recommendations
        
    except Exception as e:
        frappe.log_error(f"Error prioritizing recommendations: {str(e)}", "Prioritization Error")
        return recommendations

def store_recommendations(recommendations):
    """Store recommendations in the database"""
    try:
        stored_recommendations = []
        
        for recommendation in recommendations:
            # Check if similar recommendation already exists
            existing_recommendation = frappe.db.exists("Recommendation", {
                "metric": recommendation["metric"],
                "recommendation_type": recommendation["recommendation_type"],
                "status": ["in", ["New", "In Progress"]]
            })
            
            if existing_recommendation:
                # Update existing recommendation
                existing_doc = frappe.get_doc("Recommendation", existing_recommendation)
                
                # Only update if the new recommendation has higher priority
                if recommendation.get("priority_score", 0) > existing_doc.get("priority_score", 0):
                    existing_doc.title = recommendation["title"]
                    existing_doc.description = recommendation["description"]
                    existing_doc.priority = recommendation["priority"]
                    existing_doc.impact = json.dumps(recommendation["impact"])
                    existing_doc.suggested_actions = json.dumps(recommendation["suggested_actions"])
                    existing_doc.confidence = recommendation.get("confidence", 0.5)
                    existing_doc.modified_date = datetime.now()
                    existing_doc.save()
                    
                    stored_recommendations.append(existing_doc.name)
            else:
                # Create new recommendation
                new_recommendation = frappe.new_doc("Recommendation")
                new_recommendation.title = recommendation["title"]
                new_recommendation.description = recommendation["description"]
                new_recommendation.recommendation_type = recommendation["recommendation_type"]
                new_recommendation.priority = recommendation["priority"]
                new_recommendation.source = recommendation["source"]
                new_recommendation.source_reference = recommendation["source_reference"]
                new_recommendation.metric = recommendation["metric"]
                new_recommendation.impact = json.dumps(recommendation["impact"])
                new_recommendation.suggested_actions = json.dumps(recommendation["suggested_actions"])
                new_recommendation.confidence = recommendation.get("confidence", 0.5)
                new_recommendation.status = "New"
                new_recommendation.creation_date = datetime.now()
                new_recommendation.insert()
                
                stored_recommendations.append(new_recommendation.name)
        
        return stored_recommendations
        
    except Exception as e:
        frappe.log_error(f"Error storing recommendations: {str(e)}", "Recommendation Storage Error")
        return []

def publish_recommendation_events(recommendation_ids):
    """Publish recommendation events to Mythos EDA"""
    try:
        # Implementation would depend on Mythos EDA
        for recommendation_id in recommendation_ids:
            recommendation_doc = frappe.get_doc("Recommendation", recommendation_id)
            
            event_data = {
                "event_type": "recommendation.created",
                "recommendation_id": recommendation_doc.name,
                "title": recommendation_doc.title,
                "recommendation_type": recommendation_doc.recommendation_type,
                "priority": recommendation_doc.priority,
                "source": recommendation_doc.source,
                "metric": recommendation_doc.metric,
                "creation_date": recommendation_doc.creation_date.isoformat(),
                "status": recommendation_doc.status
            }
            
            # Placeholder for Mythos event publishing
            frappe.logger().info(f"Would publish to Mythos: {event_data}")
        
        return True
        
    except Exception as e:
        frappe.log_error(f"Error publishing recommendation events: {str(e)}", "Event Publishing Error")
        return False

def after_insert(doc, method=None):
    """Handle after_insert event for Recommendation DocType"""
    frappe.logger().info(f"Recommendation created: {doc.title}")
    
    # Publish event if configured
    if hasattr(doc, 'publish_to_mythos') and doc.publish_to_mythos:
        event_data = {
            "event_type": "recommendation.created",
            "recommendation_id": doc.name,
            "title": doc.title,
            "recommendation_type": doc.recommendation_type,
            "priority": doc.priority,
            "source": doc.source,
            "metric": doc.metric,
            "creation_date": doc.creation_date.isoformat(),
            "status": doc.status
        }
        
        # Placeholder for Mythos event publishing
        frappe.logger().info(f"Would publish to Mythos: {event_data}")

def implement_recommendation(recommendation_id, implementation_plan=None, assigned_to=None):
    """Implement a recommendation"""
    try:
        recommendation_doc = frappe.get_doc("Recommendation", recommendation_id)
        
        # Update recommendation status
        recommendation_doc.status = "In Progress"
        recommendation_doc.implementation_date = datetime.now()
        recommendation_doc.implemented_by = frappe.session.user
        
        if implementation_plan:
            recommendation_doc.implementation_plan = implementation_plan
            
        if assigned_to:
            recommendation_doc.assigned_to = assigned_to
            
        recommendation_doc.save()
        
        # Publish event if configured
        if hasattr(recommendation_doc, 'publish_to_mythos') and recommendation_doc.publish_to_mythos:
            event_data = {
                "event_type": "recommendation.implemented",
                "recommendation_id": recommendation_doc.name,
                "title": recommendation_doc.title,
                "implemented_by": recommendation_doc.implemented_by,
                "implementation_date": recommendation_doc.implementation_date.isoformat(),
                "assigned_to": recommendation_doc.assigned_to
            }
            
            # Placeholder for Mythos event publishing
            frappe.logger().info(f"Would publish to Mythos: {event_data}")
        
        return {
            "success": True,
            "recommendation": recommendation_doc.name,
            "status": recommendation_doc.status,
            "implementation_date": recommendation_doc.implementation_date
        }
        
    except Exception as e:
        frappe.log_error(f"Error implementing recommendation {recommendation_id}: {str(e)}", "Recommendation Implementation Error")
        return {
            "success": False,
            "error": str(e)
        }

def complete_recommendation(recommendation_id, outcome=None, effectiveness=None):
    """Mark a recommendation as completed"""
    try:
        recommendation_doc = frappe.get_doc("Recommendation", recommendation_id)
        
        # Update recommendation status
        recommendation_doc.status = "Completed"
        recommendation_doc.completion_date = datetime.now()
        recommendation_doc.completed_by = frappe.session.user
        
        if outcome:
            recommendation_doc.outcome = outcome
            
        if effectiveness:
            recommendation_doc.effectiveness = effectiveness
            
        recommendation_doc.save()
        
        # Publish event if configured
        if hasattr(recommendation_doc, 'publish_to_mythos') and recommendation_doc.publish_to_mythos:
            event_data = {
                "event_type": "recommendation.completed",
                "recommendation_id": recommendation_doc.name,
                "title": recommendation_doc.title,
                "completed_by": recommendation_doc.completed_by,
                "completion_date": recommendation_doc.completion_date.isoformat(),
                "effectiveness": recommendation_doc.effectiveness
            }
            
            # Placeholder for Mythos event publishing
            frappe.logger().info(f"Would publish to Mythos: {event_data}")
        
        return {
            "success": True,
            "recommendation": recommendation_doc.name,
            "status": recommendation_doc.status,
            "completion_date": recommendation_doc.completion_date
        }
        
    except Exception as e:
        frappe.log_error(f"Error completing recommendation {recommendation_id}: {str(e)}", "Recommendation Completion Error")
        return {
            "success": False,
            "error": str(e)
        }