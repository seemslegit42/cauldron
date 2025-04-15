"""
AnalyticsMetric DocType module
"""

import frappe
from frappe.model.document import Document
import json
from datetime import datetime
import re

class AnalyticsMetric(Document):
    """
    AnalyticsMetric represents a business KPI or metric definition
    """
    
    def validate(self):
        """Validate the metric configuration"""
        self.validate_calculation_method()
        self.validate_thresholds()
        
    def validate_calculation_method(self):
        """Validate calculation method details"""
        if self.calculation_method == "Direct Field":
            if not self.data_source or not self.source_field:
                frappe.throw("Data Source and Source Field are required for Direct Field calculation method")
        
        elif self.calculation_method == "Formula":
            if not self.formula:
                frappe.throw("Formula is required for Formula calculation method")
            self.validate_formula()
        
        elif self.calculation_method == "SQL Query":
            if not self.sql_query:
                frappe.throw("SQL Query is required for SQL Query calculation method")
            self.validate_sql_query()
        
        elif self.calculation_method == "Python Function":
            if not self.python_function:
                frappe.throw("Python Function is required for Python Function calculation method")
            self.validate_python_function()
    
    def validate_formula(self):
        """Validate the formula syntax"""
        if not self.formula:
            return
            
        # Basic validation - check for balanced parentheses
        if self.formula.count('(') != self.formula.count(')'):
            frappe.throw("Formula has unbalanced parentheses")
        
        # Check for valid metric references
        metric_refs = re.findall(r'\{([^}]+)\}', self.formula)
        for ref in metric_refs:
            if not frappe.db.exists("AnalyticsMetric", ref):
                frappe.throw(f"Formula references non-existent metric: {ref}")
    
    def validate_sql_query(self):
        """Validate the SQL query"""
        if not self.sql_query:
            return
            
        # Basic validation - check for SELECT statement
        if not re.match(r'^\s*SELECT', self.sql_query, re.IGNORECASE):
            frappe.throw("SQL Query must start with SELECT")
        
        # Check for potentially dangerous operations
        dangerous_patterns = [
            r'\bDROP\b', r'\bDELETE\b', r'\bTRUNCATE\b', r'\bALTER\b', 
            r'\bCREATE\b', r'\bINSERT\b', r'\bUPDATE\b', r'\bGRANT\b'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, self.sql_query, re.IGNORECASE):
                frappe.throw(f"SQL Query contains potentially dangerous operation: {pattern}")
    
    def validate_python_function(self):
        """Validate the Python function reference"""
        if not self.python_function:
            return
            
        # Check format: module.submodule.function
        if not re.match(r'^[a-zA-Z0-9_\.]+$', self.python_function):
            frappe.throw("Python Function must be in format: module.submodule.function")
    
    def validate_thresholds(self):
        """Validate threshold values"""
        if self.comparison_type == "Higher is Better":
            if self.warning_threshold and self.critical_threshold and self.warning_threshold < self.critical_threshold:
                frappe.throw("For 'Higher is Better', Warning Threshold should be higher than Critical Threshold")
        
        elif self.comparison_type == "Lower is Better":
            if self.warning_threshold and self.critical_threshold and self.warning_threshold > self.critical_threshold:
                frappe.throw("For 'Lower is Better', Warning Threshold should be lower than Critical Threshold")
    
    def before_save(self):
        """Set metadata before saving"""
        if not self.owner_user:
            self.owner_user = frappe.session.user
            
        if not self.created_date:
            self.created_date = datetime.now()
            
        self.modified_date = datetime.now()
        
        # Add audit log entry
        self.add_audit_entry()
    
    def add_audit_entry(self):
        """Add entry to audit trail"""
        audit_entry = {
            "user": frappe.session.user,
            "timestamp": datetime.now().isoformat(),
            "action": "Update" if self.get_doc_before_save() else "Create",
            "changes": self.get_changes_summary()
        }
        
        # In a real implementation, this would append to the audit_trail child table
        frappe.log_error(f"Audit entry for {self.metric_name}: {audit_entry}", "Metric Audit")
    
    def get_changes_summary(self):
        """Get summary of changes made to the document"""
        if not self.get_doc_before_save():
            return "Initial creation"
            
        old_doc = self.get_doc_before_save()
        changes = []
        
        for field in self.meta.fields:
            old_value = old_doc.get(field.fieldname)
            new_value = self.get(field.fieldname)
            
            if old_value != new_value:
                changes.append(f"{field.label}: {old_value} -> {new_value}")
        
        return ", ".join(changes) if changes else "No changes"
    
    def on_update(self):
        """Handle updates to the metric"""
        self.publish_metric_updated_event()
        self.schedule_metric_calculation()
    
    def publish_metric_updated_event(self):
        """Publish event when metric is updated"""
        if self.publish_to_mythos:
            # Implementation would depend on Mythos EDA
            event_data = {
                "metric_id": self.name,
                "metric_name": self.metric_name,
                "metric_type": self.metric_type,
                "updated_by": frappe.session.user,
                "updated_at": datetime.now().isoformat()
            }
            # Placeholder for Mythos event publishing
            frappe.log_error(f"Would publish to Mythos: {event_data}", "Metric Update")
    
    def schedule_metric_calculation(self):
        """Schedule calculation of the metric"""
        if self.is_active:
            # Implementation would depend on the scheduler being used
            frappe.enqueue(
                "cauldron_synapse.predictive_analytics.metric.calculate_metric",
                metric=self.name,
                queue="long",
                timeout=300
            )
    
    def calculate_value(self, filters=None):
        """Calculate the current value of the metric"""
        try:
            # Implementation would depend on the calculation method
            if self.calculation_method == "Direct Field":
                # Fetch value from data source
                return 100  # Placeholder value
                
            elif self.calculation_method == "Formula":
                # Evaluate formula
                return 200  # Placeholder value
                
            elif self.calculation_method == "SQL Query":
                # Execute SQL query
                return 300  # Placeholder value
                
            elif self.calculation_method == "Python Function":
                # Call Python function
                return 400  # Placeholder value
                
            return None
            
        except Exception as e:
            frappe.log_error(f"Error calculating metric {self.metric_name}: {str(e)}", "Metric Calculation Error")
            return None
    
    def get_historical_values(self, start_date, end_date, granularity="daily"):
        """Get historical values for the metric"""
        # Implementation would fetch historical values from the database
        return [
            {"date": "2023-01-01", "value": 100},
            {"date": "2023-01-02", "value": 110},
            {"date": "2023-01-03", "value": 120}
        ]  # Placeholder data
    
    def check_thresholds(self, value):
        """Check if value exceeds thresholds"""
        result = {
            "value": value,
            "target": self.target_value,
            "status": "normal"
        }
        
        if self.comparison_type == "Higher is Better":
            if self.critical_threshold and value <= self.critical_threshold:
                result["status"] = "critical"
            elif self.warning_threshold and value <= self.warning_threshold:
                result["status"] = "warning"
                
        elif self.comparison_type == "Lower is Better":
            if self.critical_threshold and value >= self.critical_threshold:
                result["status"] = "critical"
            elif self.warning_threshold and value >= self.warning_threshold:
                result["status"] = "warning"
                
        return result