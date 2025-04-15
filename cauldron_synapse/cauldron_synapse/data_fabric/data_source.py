"""
Data Source management module for the Data Fabric layer
"""

import frappe
import json
from datetime import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import requests
from urllib.parse import urlparse
import os

def refresh_data_source(data_source):
    """Refresh data from a data source"""
    try:
        if isinstance(data_source, str):
            data_source_doc = frappe.get_doc("DataSource", data_source)
        else:
            data_source_doc = data_source
            
        frappe.logger().info(f"Refreshing data source: {data_source_doc.source_name}")
        
        # Extract data based on source type
        if data_source_doc.source_type == "Internal Frappe DocType":
            data = extract_from_frappe_doctype(data_source_doc)
        elif data_source_doc.source_type == "External Database":
            data = extract_from_external_database(data_source_doc)
        elif data_source_doc.source_type == "API":
            data = extract_from_api(data_source_doc)
        elif data_source_doc.source_type == "File":
            data = extract_from_file(data_source_doc)
        elif data_source_doc.source_type == "Event Stream":
            data = extract_from_event_stream(data_source_doc)
        else:
            frappe.throw(f"Unsupported source type: {data_source_doc.source_type}")
        
        # Transform data if needed
        transformed_data = transform_data(data_source_doc, data)
        
        # Load data into storage
        load_data(data_source_doc, transformed_data)
        
        # Update last refresh timestamp
        data_source_doc.db_set("last_refresh", datetime.now())
        
        # Publish event if configured
        if data_source_doc.publish_to_mythos:
            publish_refresh_event(data_source_doc)
        
        return {
            "success": True,
            "message": f"Data source {data_source_doc.source_name} refreshed successfully",
            "rows_processed": len(transformed_data) if isinstance(transformed_data, list) else "N/A"
        }
        
    except Exception as e:
        frappe.log_error(f"Error refreshing data source {data_source}: {str(e)}", "Data Source Refresh Error")
        return {
            "success": False,
            "message": str(e)
        }

def extract_from_frappe_doctype(data_source_doc):
    """Extract data from a Frappe DocType"""
    try:
        # Parse schema to get DocType name and fields
        schema = json.loads(data_source_doc.schema_definition)
        doctype = schema.get("doctype")
        fields = schema.get("fields", ["*"])
        
        if not doctype:
            frappe.throw("Schema definition must include 'doctype' field")
        
        # Build filters if specified
        filters = {}
        if data_source_doc.filter_criteria:
            try:
                filters = json.loads(data_source_doc.filter_criteria)
            except json.JSONDecodeError:
                frappe.throw("Filter criteria must be valid JSON")
        
        # Query the DocType
        data = frappe.get_all(
            doctype,
            fields=fields,
            filters=filters,
            limit=None
        )
        
        return data
        
    except Exception as e:
        frappe.log_error(f"Error extracting from Frappe DocType: {str(e)}", "Data Extraction Error")
        raise

def extract_from_external_database(data_source_doc):
    """Extract data from an external database"""
    try:
        # Create connection string
        if data_source_doc.connection_string:
            conn_str = data_source_doc.connection_string
        else:
            # Build connection string based on connection type
            if data_source_doc.connection_type == "PostgreSQL":
                conn_str = f"postgresql://{data_source_doc.username}:{data_source_doc.password}@{data_source_doc.host}:{data_source_doc.port}/{data_source_doc.database_name}"
            elif data_source_doc.connection_type == "MySQL":
                conn_str = f"mysql+pymysql://{data_source_doc.username}:{data_source_doc.password}@{data_source_doc.host}:{data_source_doc.port}/{data_source_doc.database_name}"
            elif data_source_doc.connection_type == "MongoDB":
                # MongoDB would use a different approach, this is simplified
                conn_str = f"mongodb://{data_source_doc.username}:{data_source_doc.password}@{data_source_doc.host}:{data_source_doc.port}/{data_source_doc.database_name}"
            elif data_source_doc.connection_type == "ClickHouse":
                conn_str = f"clickhouse://{data_source_doc.username}:{data_source_doc.password}@{data_source_doc.host}:{data_source_doc.port}/{data_source_doc.database_name}"
            else:
                frappe.throw(f"Unsupported connection type: {data_source_doc.connection_type}")
        
        # Parse schema to get query
        schema = json.loads(data_source_doc.schema_definition)
        query = schema.get("query")
        
        if not query:
            frappe.throw("Schema definition must include 'query' field for external databases")
        
        # Connect to database and execute query
        engine = create_engine(conn_str)
        with engine.connect() as connection:
            result = connection.execute(text(query))
            data = [dict(row) for row in result]
        
        return data
        
    except Exception as e:
        frappe.log_error(f"Error extracting from external database: {str(e)}", "Data Extraction Error")
        raise

def extract_from_api(data_source_doc):
    """Extract data from an API"""
    try:
        # Parse schema to get API details
        schema = json.loads(data_source_doc.schema_definition)
        method = schema.get("method", "GET")
        headers = schema.get("headers", {})
        params = schema.get("params", {})
        body = schema.get("body")
        response_format = schema.get("response_format", "json")
        data_path = schema.get("data_path", "")
        
        # Add authentication if specified
        if data_source_doc.authentication_method == "Basic Auth":
            auth = (data_source_doc.username, data_source_doc.password)
        elif data_source_doc.authentication_method == "API Key":
            if "api_key_header" in schema:
                headers[schema["api_key_header"]] = data_source_doc.api_key
            else:
                params["api_key"] = data_source_doc.api_key
        else:
            auth = None
        
        # Make API request
        if method.upper() == "GET":
            response = requests.get(
                data_source_doc.api_endpoint,
                headers=headers,
                params=params,
                auth=auth,
                timeout=30
            )
        elif method.upper() == "POST":
            response = requests.post(
                data_source_doc.api_endpoint,
                headers=headers,
                params=params,
                json=body if body else None,
                auth=auth,
                timeout=30
            )
        else:
            frappe.throw(f"Unsupported HTTP method: {method}")
        
        # Check response status
        response.raise_for_status()
        
        # Parse response based on format
        if response_format.lower() == "json":
            data = response.json()
            
            # Extract data using data_path if specified
            if data_path:
                for key in data_path.split('.'):
                    if key.isdigit():
                        data = data[int(key)]
                    else:
                        data = data[key]
        elif response_format.lower() == "csv":
            data = pd.read_csv(pd.StringIO(response.text)).to_dict('records')
        elif response_format.lower() == "xml":
            # This would require additional XML parsing logic
            frappe.throw("XML response format not yet supported")
        else:
            frappe.throw(f"Unsupported response format: {response_format}")
        
        return data
        
    except Exception as e:
        frappe.log_error(f"Error extracting from API: {str(e)}", "Data Extraction Error")
        raise

def extract_from_file(data_source_doc):
    """Extract data from a file"""
    try:
        # Check if file exists
        if not os.path.exists(data_source_doc.file_path):
            frappe.throw(f"File not found: {data_source_doc.file_path}")
        
        # Read file based on format
        if data_source_doc.file_format == "CSV":
            data = pd.read_csv(data_source_doc.file_path).to_dict('records')
        elif data_source_doc.file_format == "JSON":
            with open(data_source_doc.file_path, 'r') as f:
                data = json.load(f)
        elif data_source_doc.file_format == "Excel":
            data = pd.read_excel(data_source_doc.file_path).to_dict('records')
        elif data_source_doc.file_format == "Parquet":
            data = pd.read_parquet(data_source_doc.file_path).to_dict('records')
        else:
            frappe.throw(f"Unsupported file format: {data_source_doc.file_format}")
        
        return data
        
    except Exception as e:
        frappe.log_error(f"Error extracting from file: {str(e)}", "Data Extraction Error")
        raise

def extract_from_event_stream(data_source_doc):
    """Extract data from an event stream"""
    # This would be implemented to connect to Mythos EDA
    # For now, return placeholder data
    return [{"event_id": "123", "event_type": "sample", "timestamp": datetime.now().isoformat()}]

def transform_data(data_source_doc, data):
    """Transform data based on transformation rules"""
    try:
        # Parse transformation rules if specified
        transformation_rules = None
        if data_source_doc.schema_definition:
            schema = json.loads(data_source_doc.schema_definition)
            transformation_rules = schema.get("transformations")
        
        if not transformation_rules:
            # No transformations, return data as is
            return data
        
        # Convert to pandas DataFrame for easier transformation
        df = pd.DataFrame(data)
        
        # Apply transformations
        for rule in transformation_rules:
            rule_type = rule.get("type")
            
            if rule_type == "rename":
                # Rename columns
                df = df.rename(columns=rule.get("mapping", {}))
                
            elif rule_type == "filter":
                # Filter rows
                condition = rule.get("condition")
                df = df.query(condition)
                
            elif rule_type == "calculate":
                # Add calculated column
                column = rule.get("column")
                expression = rule.get("expression")
                df[column] = df.eval(expression)
                
            elif rule_type == "type_conversion":
                # Convert column types
                for column, dtype in rule.get("conversions", {}).items():
                    df[column] = df[column].astype(dtype)
                    
            elif rule_type == "drop":
                # Drop columns
                columns = rule.get("columns", [])
                df = df.drop(columns=columns)
                
            elif rule_type == "fill_na":
                # Fill missing values
                value = rule.get("value")
                columns = rule.get("columns", df.columns.tolist())
                df[columns] = df[columns].fillna(value)
        
        # Convert back to list of dictionaries
        return df.to_dict('records')
        
    except Exception as e:
        frappe.log_error(f"Error transforming data: {str(e)}", "Data Transformation Error")
        raise

def load_data(data_source_doc, data):
    """Load data into storage"""
    try:
        # Parse storage configuration
        storage_config = None
        if data_source_doc.schema_definition:
            schema = json.loads(data_source_doc.schema_definition)
            storage_config = schema.get("storage")
        
        if not storage_config:
            # Default storage in Frappe DocType
            store_in_frappe_doctype(data_source_doc, data)
        else:
            storage_type = storage_config.get("type")
            
            if storage_type == "frappe_doctype":
                store_in_frappe_doctype(data_source_doc, data)
            elif storage_type == "database":
                store_in_database(data_source_doc, data, storage_config)
            elif storage_type == "file":
                store_in_file(data_source_doc, data, storage_config)
            else:
                frappe.throw(f"Unsupported storage type: {storage_type}")
        
        return True
        
    except Exception as e:
        frappe.log_error(f"Error loading data: {str(e)}", "Data Loading Error")
        raise

def store_in_frappe_doctype(data_source_doc, data):
    """Store data in a Frappe DocType"""
    # This would be implemented to store data in a custom DocType
    # For now, just log the intent
    frappe.logger().info(f"Would store {len(data)} records in Frappe DocType for {data_source_doc.source_name}")
    return True

def store_in_database(data_source_doc, data, storage_config):
    """Store data in a database"""
    # This would be implemented to store data in an external database
    # For now, just log the intent
    frappe.logger().info(f"Would store {len(data)} records in database for {data_source_doc.source_name}")
    return True

def store_in_file(data_source_doc, data, storage_config):
    """Store data in a file"""
    # This would be implemented to store data in a file
    # For now, just log the intent
    frappe.logger().info(f"Would store {len(data)} records in file for {data_source_doc.source_name}")
    return True

def publish_refresh_event(data_source_doc):
    """Publish event when data source is refreshed"""
    # Implementation would depend on Mythos EDA
    event_data = {
        "source_id": data_source_doc.name,
        "source_name": data_source_doc.source_name,
        "source_type": data_source_doc.source_type,
        "refresh_timestamp": datetime.now().isoformat(),
        "status": "success"
    }
    # Placeholder for Mythos event publishing
    frappe.logger().info(f"Would publish to Mythos: {event_data}")
    return True

def after_insert(doc, method=None):
    """Handle after_insert event for DataSource DocType"""
    frappe.logger().info(f"DataSource created: {doc.source_name}")
    
    # Schedule initial data refresh if active
    if doc.is_active and doc.refresh_frequency != "Manual":
        frappe.enqueue(
            "cauldron_synapse.data_fabric.data_source.refresh_data_source",
            data_source=doc.name,
            queue="long",
            timeout=1500
        )

def on_update(doc, method=None):
    """Handle on_update event for DataSource DocType"""
    frappe.logger().info(f"DataSource updated: {doc.source_name}")
    
    # Schedule data refresh if active and configuration changed
    old_doc = doc.get_doc_before_save()
    if doc.is_active and doc.refresh_frequency != "Manual":
        if (not old_doc or 
            old_doc.source_type != doc.source_type or
            old_doc.connection_type != doc.connection_type or
            old_doc.schema_definition != doc.schema_definition or
            old_doc.filter_criteria != doc.filter_criteria or
            old_doc.is_active != doc.is_active):
            
            frappe.enqueue(
                "cauldron_synapse.data_fabric.data_source.refresh_data_source",
                data_source=doc.name,
                queue="long",
                timeout=1500
            )

def on_cancel(doc, method=None):
    """Handle on_cancel event for DataSource DocType"""
    frappe.logger().info(f"DataSource cancelled: {doc.source_name}")

def on_trash(doc, method=None):
    """Handle on_trash event for DataSource DocType"""
    frappe.logger().info(f"DataSource deleted: {doc.source_name}")
    
    # Clean up any associated data
    # This would be implemented based on storage configuration
    frappe.logger().info(f"Would clean up data for {doc.source_name}")