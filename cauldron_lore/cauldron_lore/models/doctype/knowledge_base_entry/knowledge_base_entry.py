import frappe
import json
import uuid
from frappe.model.document import Document
from frappe.utils import now_datetime

class KnowledgeBaseEntry(Document):
    def before_save(self):
        """Set metadata before saving"""
        if not self.creation_date:
            self.creation_date = now_datetime()
            self.created_by = frappe.session.user
        
        self.modified_date = now_datetime()
        self.modified_by = frappe.session.user
        
        # If this is a new entry or content has changed, mark embedding as outdated
        if not self.get("name") or self.has_value_changed("content"):
            self.embedding_status = "Outdated"
    
    def after_insert(self):
        """Queue embedding generation after insert"""
        self.queue_embedding_generation()
    
    def on_update(self):
        """Handle updates to the document"""
        # If content has changed, queue embedding regeneration
        if self.embedding_status == "Outdated":
            self.queue_embedding_generation()
        
        # Publish to Mythos if enabled
        if self.publish_to_mythos:
            self.publish_mythos_event("knowledge_base_entry.updated")
    
    def on_trash(self):
        """Handle document deletion"""
        # Delete vector embeddings if they exist
        if self.vector_id:
            self.delete_vector_embeddings()
        
        # Publish deletion event to Mythos if enabled
        if self.publish_to_mythos:
            self.publish_mythos_event("knowledge_base_entry.deleted")
    
    def queue_embedding_generation(self):
        """Queue the embedding generation process"""
        self.embedding_status = "Processing"
        frappe.db.commit()
        
        # Queue the embedding generation task
        frappe.enqueue(
            "cauldron_lore.lore.vector_utils.generate_embeddings_for_entry",
            queue="long",
            entry_name=self.name,
            timeout=600
        )
    
    def delete_vector_embeddings(self):
        """Delete vector embeddings for this entry"""
        # This would call the vector database utility to delete embeddings
        frappe.enqueue(
            "cauldron_lore.lore.vector_utils.delete_embeddings_for_entry",
            queue="long",
            entry_name=self.name,
            vector_id=self.vector_id,
            chunk_ids=json.loads(self.chunk_ids) if self.chunk_ids else []
        )
    
    def publish_mythos_event(self, event_type):
        """Publish an event to Mythos EDA"""
        if not self.mythos_event_topic:
            return
        
        event_data = {
            "event_type": event_type,
            "entry_id": self.name,
            "title": self.title,
            "knowledge_type": self.knowledge_type,
            "status": self.status,
            "modified_by": self.modified_by,
            "modified_date": str(self.modified_date),
            "version": self.version,
            "categories": [cat.category for cat in self.categories] if self.categories else [],
            "tags": [tag.tag for tag in self.tags] if self.tags else [],
            "vector_id": self.vector_id,
            "agent_managed": self.agent_managed,
            "managing_agent": self.managing_agent if self.agent_managed else None
        }
        
        try:
            # This would call the Mythos EDA utility to publish the event
            frappe.enqueue(
                "cauldron_lore.integrations.mythos.publish_event",
                queue="short",
                topic=self.mythos_event_topic,
                event_data=event_data
            )
        except Exception as e:
            frappe.log_error(f"Failed to publish Mythos event for {self.name}: {str(e)}")
    
    @frappe.whitelist()
    def generate_summary(self):
        """Generate a summary of the content using AI"""
        if not self.content:
            frappe.throw("Content is required to generate a summary")
        
        try:
            # This would call an AI service to generate a summary
            frappe.enqueue(
                "cauldron_lore.lore.ai_utils.generate_summary_for_entry",
                queue="long",
                entry_name=self.name,
                content=self.content
            )
            return {"status": "success", "message": "Summary generation queued"}
        except Exception as e:
            frappe.log_error(f"Failed to generate summary for {self.name}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @frappe.whitelist()
    def find_related_entries(self):
        """Find related knowledge base entries using vector similarity"""
        if not self.vector_id:
            frappe.throw("Vector embeddings must be generated first")
        
        try:
            # This would call the vector database utility to find similar entries
            frappe.enqueue(
                "cauldron_lore.lore.vector_utils.find_related_entries",
                queue="short",
                entry_name=self.name,
                vector_id=self.vector_id
            )
            return {"status": "success", "message": "Related entries search queued"}
        except Exception as e:
            frappe.log_error(f"Failed to find related entries for {self.name}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @frappe.whitelist()
    def request_agent_update(self):
        """Request an agent to update this knowledge base entry"""
        if not self.agent_managed:
            frappe.throw("This entry is not configured for agent management")
        
        if not self.managing_agent:
            frappe.throw("No managing agent specified")
        
        try:
            # This would publish a task to AetherCore via Mythos
            task_data = {
                "task_type": "knowledge_entry_update",
                "entry_id": self.name,
                "agent_id": self.managing_agent,
                "priority": "medium",
                "context": {
                    "title": self.title,
                    "knowledge_type": self.knowledge_type,
                    "current_content": self.content,
                    "current_summary": self.summary,
                    "categories": [cat.category for cat in self.categories] if self.categories else [],
                    "tags": [tag.tag for tag in self.tags] if self.tags else []
                }
            }
            
            frappe.enqueue(
                "cauldron_lore.integrations.aethercore.publish_agent_task",
                queue="short",
                task_data=task_data
            )
            
            # Update agent action tracking
            self.last_agent_action = "update_requested"
            self.last_agent_action_date = now_datetime()
            self.save(ignore_permissions=True)
            
            return {"status": "success", "message": "Agent update requested"}
        except Exception as e:
            frappe.log_error(f"Failed to request agent update for {self.name}: {str(e)}")
            return {"status": "error", "message": str(e)}