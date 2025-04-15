"""
Agent Communication Module for AetherCore

This module provides the communication infrastructure for agents in the hierarchy,
implementing the patterns defined in the Agent Interaction Playbook.
"""

import json
import logging
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

# Local imports
from ..models.agent_hierarchy import (
    AgentLevel, AgentDomain, AgentStatus, AgentBase,
    CoreSentienceAgent, DomainRegent, TaskMaster, Minion
)


class MessageType(str, Enum):
    """Enumeration of message types for agent communication"""
    TASK_ASSIGNMENT = "task_assignment"
    STATUS_UPDATE = "status_update"
    RESULT = "result"
    ERROR = "error"
    HITL_REQUEST = "hitl_request"
    HITL_RESPONSE = "hitl_response"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    RESOURCE_REQUEST = "resource_request"
    COORDINATION = "coordination"


class TaskStatus(str, Enum):
    """Enumeration of task statuses"""
    RECEIVED = "received"
    IN_PROGRESS = "in_progress"
    AWAITING_HITL = "awaiting_hitl"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class Message:
    """Base class for agent communication messages"""
    
    def __init__(
        self,
        message_id: str = None,
        message_type: MessageType = None,
        sender_id: str = None,
        sender_level: AgentLevel = None,
        recipient_id: str = None,
        recipient_level: AgentLevel = None,
        timestamp: str = None,
        payload: Dict[str, Any] = None
    ):
        self.message_id = message_id or str(uuid.uuid4())
        self.message_type = message_type
        self.sender_id = sender_id
        self.sender_level = sender_level
        self.recipient_id = recipient_id
        self.recipient_level = recipient_level
        self.timestamp = timestamp or datetime.now().isoformat()
        self.payload = payload or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value if self.message_type else None,
            "sender_id": self.sender_id,
            "sender_level": self.sender_level.value if self.sender_level else None,
            "recipient_id": self.recipient_id,
            "recipient_level": self.recipient_level.value if self.recipient_level else None,
            "timestamp": self.timestamp,
            "payload": self.payload
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        return cls(
            message_id=data.get("message_id"),
            message_type=MessageType(data.get("message_type")) if data.get("message_type") else None,
            sender_id=data.get("sender_id"),
            sender_level=AgentLevel(data.get("sender_level")) if data.get("sender_level") else None,
            recipient_id=data.get("recipient_id"),
            recipient_level=AgentLevel(data.get("recipient_level")) if data.get("recipient_level") else None,
            timestamp=data.get("timestamp"),
            payload=data.get("payload", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create message from JSON string"""
        return cls.from_dict(json.loads(json_str))


class TaskAssignmentMessage(Message):
    """Message for assigning tasks to agents"""
    
    def __init__(
        self,
        task_id: str = None,
        task_type: str = None,
        task_description: str = None,
        priority: int = 5,  # 1-10, 10 being highest
        input_data: Dict[str, Any] = None,
        max_retries: int = 3,
        timeout_seconds: int = 3600,
        **kwargs
    ):
        super().__init__(message_type=MessageType.TASK_ASSIGNMENT, **kwargs)
        
        # Task-specific fields
        self.payload["task_id"] = task_id or str(uuid.uuid4())
        self.payload["task_type"] = task_type
        self.payload["task_description"] = task_description
        self.payload["priority"] = priority
        self.payload["input_data"] = input_data or {}
        self.payload["max_retries"] = max_retries
        self.payload["timeout_seconds"] = timeout_seconds


class StatusUpdateMessage(Message):
    """Message for reporting agent status updates"""
    
    def __init__(
        self,
        task_id: str = None,
        status: TaskStatus = None,
        progress: float = None,  # 0.0 to 1.0
        details: str = None,
        **kwargs
    ):
        super().__init__(message_type=MessageType.STATUS_UPDATE, **kwargs)
        
        # Status-specific fields
        self.payload["task_id"] = task_id
        self.payload["status"] = status.value if status else None
        self.payload["progress"] = progress
        self.payload["details"] = details


class ResultMessage(Message):
    """Message for reporting task results"""
    
    def __init__(
        self,
        task_id: str = None,
        result_data: Dict[str, Any] = None,
        execution_time_ms: int = None,
        metrics: Dict[str, Any] = None,
        **kwargs
    ):
        super().__init__(message_type=MessageType.RESULT, **kwargs)
        
        # Result-specific fields
        self.payload["task_id"] = task_id
        self.payload["result_data"] = result_data or {}
        self.payload["execution_time_ms"] = execution_time_ms
        self.payload["metrics"] = metrics or {}


class ErrorMessage(Message):
    """Message for reporting errors"""
    
    def __init__(
        self,
        task_id: str = None,
        error_type: str = None,
        error_message: str = None,
        error_details: Dict[str, Any] = None,
        retry_count: int = None,
        **kwargs
    ):
        super().__init__(message_type=MessageType.ERROR, **kwargs)
        
        # Error-specific fields
        self.payload["task_id"] = task_id
        self.payload["error_type"] = error_type
        self.payload["error_message"] = error_message
        self.payload["error_details"] = error_details or {}
        self.payload["retry_count"] = retry_count


class HITLRequestMessage(Message):
    """Message for requesting human-in-the-loop intervention"""
    
    def __init__(
        self,
        task_id: str = None,
        request_type: str = None,  # e.g., "approval", "guidance", "exception"
        request_description: str = None,
        options: List[Dict[str, Any]] = None,
        timeout_seconds: int = 3600,
        urgency: str = "normal",  # "low", "normal", "high", "critical"
        **kwargs
    ):
        super().__init__(message_type=MessageType.HITL_REQUEST, **kwargs)
        
        # HITL request-specific fields
        self.payload["task_id"] = task_id
        self.payload["request_type"] = request_type
        self.payload["request_description"] = request_description
        self.payload["options"] = options or []
        self.payload["timeout_seconds"] = timeout_seconds
        self.payload["urgency"] = urgency


class HITLResponseMessage(Message):
    """Message for responding to human-in-the-loop requests"""
    
    def __init__(
        self,
        task_id: str = None,
        request_id: str = None,
        response: str = None,  # e.g., "approved", "rejected", "guidance"
        response_details: Dict[str, Any] = None,
        human_id: str = None,
        **kwargs
    ):
        super().__init__(message_type=MessageType.HITL_RESPONSE, **kwargs)
        
        # HITL response-specific fields
        self.payload["task_id"] = task_id
        self.payload["request_id"] = request_id
        self.payload["response"] = response
        self.payload["response_details"] = response_details or {}
        self.payload["human_id"] = human_id


class KnowledgeSharingMessage(Message):
    """Message for sharing knowledge between agents"""
    
    def __init__(
        self,
        knowledge_type: str = None,  # e.g., "insight", "pattern", "warning"
        knowledge_content: Dict[str, Any] = None,
        confidence: float = None,  # 0.0 to 1.0
        source_context: Dict[str, Any] = None,
        **kwargs
    ):
        super().__init__(message_type=MessageType.KNOWLEDGE_SHARING, **kwargs)
        
        # Knowledge sharing-specific fields
        self.payload["knowledge_type"] = knowledge_type
        self.payload["knowledge_content"] = knowledge_content or {}
        self.payload["confidence"] = confidence
        self.payload["source_context"] = source_context or {}


class ResourceRequestMessage(Message):
    """Message for requesting resources"""
    
    def __init__(
        self,
        resource_type: str = None,  # e.g., "computational", "data", "tool_access"
        resource_details: Dict[str, Any] = None,
        justification: str = None,
        priority: int = 5,  # 1-10, 10 being highest
        **kwargs
    ):
        super().__init__(message_type=MessageType.RESOURCE_REQUEST, **kwargs)
        
        # Resource request-specific fields
        self.payload["resource_type"] = resource_type
        self.payload["resource_details"] = resource_details or {}
        self.payload["justification"] = justification
        self.payload["priority"] = priority


class CoordinationMessage(Message):
    """Message for coordinating between agents"""
    
    def __init__(
        self,
        coordination_type: str = None,  # e.g., "delegation", "collaboration", "conflict_resolution"
        coordination_details: Dict[str, Any] = None,
        related_task_ids: List[str] = None,
        **kwargs
    ):
        super().__init__(message_type=MessageType.COORDINATION, **kwargs)
        
        # Coordination-specific fields
        self.payload["coordination_type"] = coordination_type
        self.payload["coordination_details"] = coordination_details or {}
        self.payload["related_task_ids"] = related_task_ids or []


class MessageBroker:
    """Message broker for agent communication"""
    
    def __init__(self, broker_type: str = "memory", config: Dict[str, Any] = None):
        """Initialize the message broker
        
        Args:
            broker_type: Type of broker to use ("memory", "kafka", or "rabbitmq")
            config: Configuration for the broker
        """
        self.logger = logging.getLogger(__name__)
        self.broker_type = broker_type
        self.config = config or {}
        
        # In-memory queues and subscribers (used for memory broker)
        self.queues = {}
        self.subscribers = {}
        
        # Kafka producer and consumer (used for Kafka broker)
        self.kafka_producer = None
        self.kafka_consumers = {}
        
        # Initialize broker
        if broker_type == "kafka":
            self._init_kafka()
        elif broker_type == "rabbitmq":
            self._init_rabbitmq()
        else:
            self.logger.info("Using in-memory message broker")
    
    def _init_kafka(self):
        """Initialize Kafka producer and consumer"""
        try:
            from kafka import KafkaProducer, KafkaConsumer
            import json
            
            # Get Kafka configuration
            bootstrap_servers = self.config.get("bootstrap_servers", "localhost:9092")
            
            # Create Kafka producer
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks="all",
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            
            self.logger.info(f"Initialized Kafka producer with bootstrap servers: {bootstrap_servers}")
            
        except ImportError:
            self.logger.error("Kafka-python package not installed. Please install it to use Kafka broker.")
            self.broker_type = "memory"
        except Exception as e:
            self.logger.error(f"Error initializing Kafka: {str(e)}")
            self.broker_type = "memory"
    
    def _init_rabbitmq(self):
        """Initialize RabbitMQ connection"""
        try:
            import pika
            
            # Get RabbitMQ configuration
            host = self.config.get("host", "localhost")
            port = self.config.get("port", 5672)
            virtual_host = self.config.get("virtual_host", "/")
            username = self.config.get("username", "guest")
            password = self.config.get("password", "guest")
            
            # Create RabbitMQ connection
            credentials = pika.PlainCredentials(username, password)
            parameters = pika.ConnectionParameters(
                host=host,
                port=port,
                virtual_host=virtual_host,
                credentials=credentials
            )
            self.rabbitmq_connection = pika.BlockingConnection(parameters)
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            
            self.logger.info(f"Initialized RabbitMQ connection to {host}:{port}")
            
        except ImportError:
            self.logger.error("Pika package not installed. Please install it to use RabbitMQ broker.")
            self.broker_type = "memory"
        except Exception as e:
            self.logger.error(f"Error initializing RabbitMQ: {str(e)}")
            self.broker_type = "memory"
    
    def publish(self, topic: str, message: Message) -> bool:
        """Publish a message to a topic"""
        try:
            if self.broker_type == "kafka" and self.kafka_producer:
                # Publish to Kafka
                future = self.kafka_producer.send(
                    topic,
                    value=message.to_dict()
                )
                # Wait for the message to be sent
                future.get(timeout=10)
                self.logger.debug(f"Published message {message.message_id} to Kafka topic {topic}")
                return True
                
            elif self.broker_type == "rabbitmq" and hasattr(self, "rabbitmq_channel"):
                # Publish to RabbitMQ
                import json
                
                # Declare exchange
                self.rabbitmq_channel.exchange_declare(
                    exchange=topic,
                    exchange_type="fanout",
                    durable=True
                )
                
                # Publish message
                self.rabbitmq_channel.basic_publish(
                    exchange=topic,
                    routing_key="",
                    body=json.dumps(message.to_dict()),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                        content_type="application/json"
                    )
                )
                
                self.logger.debug(f"Published message {message.message_id} to RabbitMQ exchange {topic}")
                return True
                
            else:
                # Use in-memory queue
                # Create queue if it doesn't exist
                if topic not in self.queues:
                    self.queues[topic] = []
                
                # Add message to queue
                self.queues[topic].append(message)
                
                # Notify subscribers
                if topic in self.subscribers:
                    for callback in self.subscribers[topic]:
                        try:
                            callback(message)
                        except Exception as e:
                            self.logger.error(f"Error in subscriber callback: {str(e)}")
                
                self.logger.debug(f"Published message {message.message_id} to in-memory topic {topic}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error publishing message: {str(e)}")
            return False
    
    def subscribe(self, topic: str, callback: callable) -> bool:
        """Subscribe to a topic"""
        try:
            if self.broker_type == "kafka":
                # Subscribe to Kafka topic
                from kafka import KafkaConsumer
                import json
                import threading
                
                # Get Kafka configuration
                bootstrap_servers = self.config.get("bootstrap_servers", "localhost:9092")
                group_id = self.config.get("group_id", "aether_core")
                
                # Create consumer
                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=bootstrap_servers,
                    group_id=f"{group_id}_{topic}",
                    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                    auto_offset_reset="latest",
                    enable_auto_commit=True
                )
                
                # Start consumer thread
                def consume():
                    for msg in consumer:
                        try:
                            # Convert message to Message object
                            message = Message.from_dict(msg.value)
                            # Call callback
                            callback(message)
                        except Exception as e:
                            self.logger.error(f"Error processing Kafka message: {str(e)}")
                
                thread = threading.Thread(target=consume, daemon=True)
                thread.start()
                
                # Store consumer and thread
                self.kafka_consumers[topic] = {
                    "consumer": consumer,
                    "thread": thread,
                    "callback": callback
                }
                
                self.logger.debug(f"Subscribed to Kafka topic {topic}")
                return True
                
            elif self.broker_type == "rabbitmq" and hasattr(self, "rabbitmq_channel"):
                # Subscribe to RabbitMQ exchange
                import json
                import threading
                
                # Declare exchange
                self.rabbitmq_channel.exchange_declare(
                    exchange=topic,
                    exchange_type="fanout",
                    durable=True
                )
                
                # Declare queue
                result = self.rabbitmq_channel.queue_declare(queue="", exclusive=True)
                queue_name = result.method.queue
                
                # Bind queue to exchange
                self.rabbitmq_channel.queue_bind(
                    exchange=topic,
                    queue=queue_name
                )
                
                # Define callback
                def on_message(ch, method, properties, body):
                    try:
                        # Convert message to Message object
                        message_dict = json.loads(body)
                        message = Message.from_dict(message_dict)
                        # Call callback
                        callback(message)
                    except Exception as e:
                        self.logger.error(f"Error processing RabbitMQ message: {str(e)}")
                
                # Start consuming
                self.rabbitmq_channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=on_message,
                    auto_ack=True
                )
                
                # Start consumer thread
                def consume():
                    self.rabbitmq_channel.start_consuming()
                
                thread = threading.Thread(target=consume, daemon=True)
                thread.start()
                
                self.logger.debug(f"Subscribed to RabbitMQ exchange {topic}")
                return True
                
            else:
                # Use in-memory subscription
                # Create subscriber list if it doesn't exist
                if topic not in self.subscribers:
                    self.subscribers[topic] = []
                
                # Add callback to subscriber list
                self.subscribers[topic].append(callback)
                
                self.logger.debug(f"Subscribed to in-memory topic {topic}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error subscribing to topic: {str(e)}")
            return False
    
    def unsubscribe(self, topic: str, callback: callable) -> bool:
        """Unsubscribe from a topic"""
        try:
            if self.broker_type == "kafka":
                # Unsubscribe from Kafka topic
                if topic in self.kafka_consumers and self.kafka_consumers[topic]["callback"] == callback:
                    # Close consumer
                    self.kafka_consumers[topic]["consumer"].close()
                    # Remove from consumers
                    del self.kafka_consumers[topic]
                    
                    self.logger.debug(f"Unsubscribed from Kafka topic {topic}")
                    return True
                
                return False
                
            elif self.broker_type == "rabbitmq":
                # Unsubscribing from RabbitMQ is more complex and would require
                # tracking consumer tags. For simplicity, we'll just log a warning.
                self.logger.warning(f"Unsubscribing from RabbitMQ topic {topic} is not fully implemented")
                return False
                
            else:
                # Use in-memory unsubscription
                # Check if topic exists
                if topic not in self.subscribers:
                    return False
                
                # Remove callback from subscriber list
                if callback in self.subscribers[topic]:
                    self.subscribers[topic].remove(callback)
                    
                    self.logger.debug(f"Unsubscribed from in-memory topic {topic}")
                    
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Error unsubscribing from topic: {str(e)}")
            return False
    
    def get_messages(self, topic: str, max_count: int = None) -> List[Message]:
        """Get messages from a topic queue (only works for in-memory broker)"""
        try:
            if self.broker_type != "memory":
                self.logger.warning("get_messages() is only supported for in-memory broker")
                return []
                
            # Check if topic exists
            if topic not in self.queues:
                return []
            
            # Get messages
            if max_count is None:
                messages = self.queues[topic].copy()
            else:
                messages = self.queues[topic][:max_count]
            
            return messages
            
        except Exception as e:
            self.logger.error(f"Error getting messages: {str(e)}")
            return []
    
    def clear_queue(self, topic: str) -> bool:
        """Clear a topic queue (only works for in-memory broker)"""
        try:
            if self.broker_type != "memory":
                self.logger.warning("clear_queue() is only supported for in-memory broker")
                return False
                
            # Check if topic exists
            if topic not in self.queues:
                return False
            
            # Clear queue
            self.queues[topic] = []
            
            self.logger.debug(f"Cleared queue for topic {topic}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing queue: {str(e)}")
            return False
            
    def close(self):
        """Close connections"""
        try:
            if self.broker_type == "kafka" and self.kafka_producer:
                self.kafka_producer.close()
                for topic, data in self.kafka_consumers.items():
                    data["consumer"].close()
                
            elif self.broker_type == "rabbitmq" and hasattr(self, "rabbitmq_connection"):
                self.rabbitmq_connection.close()
                
            self.logger.info(f"Closed {self.broker_type} message broker connections")
            
        except Exception as e:
            self.logger.error(f"Error closing message broker connections: {str(e)}")