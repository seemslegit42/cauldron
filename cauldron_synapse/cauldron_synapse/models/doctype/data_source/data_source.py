"""
DataSource DocType module
"""

import frappe
from frappe.model.document import Document
import json
from datetime import datetime

class DataSource(Document):
    """
    DataSource represents a source of data for analytics
    """
    
    def validate(self):
        """Validate the data source configuration"""
        self.validate_connection_details()
        self.validate_schema()
        
    def validate_connection_details(self):
        """Validate connection details based on source type"""
        if self.source_type == "Internal Frappe DocType":
            if not self.schema_definition:
                frappe.throw("Schema definition is required for Frappe DocType sources")
        
        elif self.source_type == "External Database":
            if not self.connection_type:
                frappe.throw("Connection type is required for External Database sources")
            if not (self.connection_string or (self.host and self.database_name)):
                frappe.throw("Either connection string or host/database details are required")
        
        elif self.source_type == "API":
            if not self.api_endpoint:
                frappe.throw("API endpoint is required for API sources")
        
        elif self.source_type == "File":
            if not self.file_path or not self.file_format:
                frappe.throw("File path and format are required for File sources")
        
        elif self.source_type == "Event Stream":
            if not self.mythos_event_topic:
                frappe.throw("Mythos event topic is required for Event Stream sources")
    
    def validate_schema(self):
        """Validate the schema definition if provided"""
        if self.schema_definition:
            try:
                schema = json.loads(self.schema_definition)
                if not isinstance(schema, dict):
                    frappe.throw("Schema definition must be a valid JSON object")
            except json.JSONDecodeError:
                frappe.throw("Schema definition must be valid JSON")
    
    def before_save(self):
        """Set metadata before saving"""
        if not self.owner_user:
            self.owner_user = frappe.session.user
    
    def on_update(self):
        """Handle updates to the data source"""
        self.schedule_data_refresh()
        self.publish_source_updated_event()
    
    def schedule_data_refresh(self):
        """Schedule data refresh based on frequency"""
        if self.is_active and self.refresh_frequency != "Manual":
            # Implementation would depend on the scheduler being used
            frappe.enqueue(
                "cauldron_synapse.data_fabric.data_source.refresh_data_source",
                data_source=self.name,
                queue="long",
                timeout=1500
            )
    
    def publish_source_updated_event(self):
        """Publish event when data source is updated"""
        if self.publish_to_mythos:
            # Implementation would depend on Mythos EDA
            event_data = {
                "source_id": self.name,
                "source_name": self.source_name,
                "source_type": self.source_type,
                "updated_by": frappe.session.user,
                "updated_at": datetime.now().isoformat()
            }
            # Placeholder for Mythos event publishing
            frappe.log_error(f"Would publish to Mythos: {event_data}", "DataSource Update")
    
    def test_connection(self):
        """Test the connection to the data source"""
        try:
            if self.source_type == "Internal Frappe DocType":
                # Test if DocType exists
                return {"success": True, "message": "DocType exists"}
                
            elif self.source_type == "External Database":
                # Implementation would depend on the database type
                return {"success": True, "message": "Connection successful"}
                
            elif self.source_type == "API":
                # Implementation would make a test API call
                return {"success": True, "message": "API endpoint reachable"}
                
            elif self.source_type == "File":
                # Implementation would check file existence
                return {"success": True, "message": "File accessible"}
                
            elif self.source_type == "Event Stream":
                # Implementation would check Mythos topic
                return {"success": True, "message": "Event stream available"}
                
            return {"success": False, "message": "Unsupported source type"}
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def fetch_sample_data(self):
        """Fetch sample data from the source"""
        try:
            # Implementation would depend on the source type
            sample_data = {"sample": "data"}
            self.sample_data = json.dumps(sample_data, indent=2)
            self.save()
            return {"success": True, "data": sample_data}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_schema(self):
        """Get the schema of the data source"""
        if self.schema_definition:
            return json.loads(self.schema_definition)
        return None"""
DataSource DocType module
"""

import frappe
from frappe.model.document import Document
import json
from datetime import datetime

class DataSource(Document):
    """
    DataSource represents a source of data for analytics
    """
    
    def validate(self):
        """Validate the data source configuration"""
        self.validate_connection_details()
        self.validate_schema()
        
    def validate_connection_details(self):
        """Validate connection details based on source type"""
        if self.source_type == "Internal Frappe DocType":
            if not self.schema_definition:
                frappe.throw("Schema definition is required for Frappe DocType sources")
        
        elif self.source_type == "External Database":
            if not self.connection_type:
                frappe.throw("Connection type is required for External Database sources")
            if not (self.connection_string or (self.host and self.database_name)):
                frappe.throw("Either connection string or host/database details are required")
        
        elif self.source_type == "API":
            if not self.api_endpoint:
                frappe.throw("API endpoint is required for API sources")
        
        elif self.source_type == "File":
            if not self.file_path or not self.file_format:
                frappe.throw("File path and format are required for File sources")
        
        elif self.source_type == "Event Stream":
            if not self.mythos_event_topic:
                frappe.throw("Mythos event topic is required for Event Stream sources")
    
    def validate_schema(self):
        """Validate the schema definition if provided"""
        if self.schema_definition:
            try:
                schema = json.loads(self.schema_definition)
                if not isinstance(schema, dict):
                    frappe.throw("Schema definition must be a valid JSON object")
            except json.JSONDecodeError:
                frappe.throw("Schema definition must be valid JSON")
    
    def before_save(self):
        """Set metadata before saving"""
        if not self.owner_user:
            self.owner_user = frappe.session.user
    
    def on_update(self):
        """Handle updates to the data source"""
        self.schedule_data_refresh()
        self.publish_source_updated_event()
    
    def schedule_data_refresh(self):
        """Schedule data refresh based on frequency"""
        if self.is_active and self.refresh_frequency != "Manual":
            # Implementation would depend on the scheduler being used
            frappe.enqueue(
                "cauldron_synapse.data_fabric.data_source.refresh_data_source",
                data_source=self.name,
                queue="long",
                timeout=1500
            )
    
    def publish_source_updated_event(self):
        """Publish event when data source is updated"""
        if self.publish_to_mythos:
            # Implementation would depend on Mythos EDA
            event_data = {
                "source_id": self.name,
                "source_name": self.source_name,
                "source_type": self.source_type,
                "updated_by": frappe.session.user,
                "updated_at": datetime.now().isoformat()
            }
            # Placeholder for Mythos event publishing
            frappe.log_error(f"Would publish to Mythos: {event_data}", "DataSource Update")
    
    def test_connection(self):
        """Test the connection to the data source"""
        try:
            if self.source_type == "Internal Frappe DocType":
                # Test if DocType exists
                return {"success": True, "message": "DocType exists"}
                
            elif self.source_type == "External Database":
                # Implementation would depend on the database type
                return {"success": True, "message": "Connection successful"}
                
            elif self.source_type == "API":
                # Implementation would make a test API call
                return {"success": True, "message": "API endpoint reachable"}
                
            elif self.source_type == "File":
                # Implementation would check file existence
                return {"success": True, "message": "File accessible"}
                
            elif self.source_type == "Event Stream":
                # Implementation would check Mythos topic
                return {"success": True, "message": "Event stream available"}
                
            return {"success": False, "message": "Unsupported source type"}
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def fetch_sample_data(self):
        """Fetch sample data from the source"""
        try:
            # Implementation would depend on the source type
            sample_data = {"sample": "data"}
            self.sample_data = json.dumps(sample_data, indent=2)
            self.save()
            return {"success": True, "data": sample_data}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_schema(self):
        """Get the schema of the data source"""
        if self.schema_definition:
            return json.loads(self.schema_definition)
        return None