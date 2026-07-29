#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Workflow Engine
Visual workflow representation, building, and execution.
"""

import os
import sys
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.sales-automation.workflow")


class WorkflowNodeType(Enum):
    VALIDATION = "validation"
    DECISION = "decision"
    APPROVAL = "approval"
    DELAY = "delay"
    PUBLISH = "publish"
    SYNCHRONIZE = "synchronize"
    NOTIFICATION = "notification"
    RETRY = "retry"
    TERMINATE = "terminate"


class WorkflowStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowNode:
    """Workflow node definition"""
    node_id: str
    type: str
    name: str
    config: Dict[str, Any]
    next_nodes: List[str]
    retry_policy: Dict[str, Any]


@dataclass
class WorkflowDefinition:
    """Workflow definition"""
    workflow_id: str
    name: str
    description: str
    version: str
    nodes: List[WorkflowNode]
    entry_node: str
    exit_node: str
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str


@dataclass
class WorkflowExecution:
    """Workflow execution instance"""
    execution_id: str
    workflow_id: str
    status: str
    current_node: str
    context: Dict[str, Any]
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]
    retry_count: int
    created_at: str


class WorkflowBuilder:
    """Build workflow definitions programmatically"""
    
    def __init__(self):
        self._nodes: Dict[str, WorkflowNode] = {}
        self._edges: List[tuple] = []
        self._entry_node: Optional[str] = None
        self._exit_node: Optional[str] = None
    
    def add_node(self, node_id: str, node_type: str, name: str, 
                 config: Dict[str, Any] = None, next_nodes: List[str] = None,
                 retry_policy: Dict[str, Any] = None) -> 'WorkflowBuilder':
        self._nodes[node_id] = WorkflowNode(
            node_id=node_id,
            type=node_type,
            name=name,
            config=config or {},
            next_nodes=next_nodes or [],
            retry_policy=retry_policy or {}
        )
        return self
    
    def set_entry(self, node_id: str) -> 'WorkflowBuilder':
        self._entry_node = node_id
        return self
    
    def set_exit(self, node_id: str) -> 'WorkflowBuilder':
        self._exit_node = node_id
        return self
    
    def build(self, name: str, description: str = "") -> WorkflowDefinition:
        return WorkflowDefinition(
            workflow_id=f"wf-{uuid.uuid4().hex[:12]}",
            name=name,
            description=description,
            version="1.0.0",
            nodes=list(self._nodes.values()),
            entry_node=self._entry_node,
            exit_node=self._exit_node,
            metadata={},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )


class WorkflowEngine:
    """Execute workflow definitions"""
    
    def __init__(self, db_manager, event_bus, publication_engine, notification_engine):
        self.db = db_manager
        self.event_bus = event_bus
        self.publication_engine = publication_engine
        self.notification_engine = notification_engine
        self._active_executions: Dict[str, WorkflowExecution] = {}
    
    def start_workflow(self, workflow_id: str, context: Dict[str, Any]) -> Optional[str]:
        try:
            execution_id = f"exec-{uuid.uuid4().hex[:12]}"
            workflow = self._load_workflow(workflow_id)
            
            if not workflow:
                logger.error(f"Workflow not found: {workflow_id}")
                return None
            
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.RUNNING.value,
                current_node=workflow.entry_node,
                context=context,
                started_at=datetime.now().isoformat(),
                completed_at=None,
                error_message=None,
                retry_count=0,
                created_at=datetime.now().isoformat()
            )
            
            self._active_executions[execution_id] = execution
            self._save_execution(execution)
            
            logger.info(f"Workflow started: {execution_id}")
            return execution_id
        except Exception as e:
            logger.error(f"Failed to start workflow: {e}")
            return None
    
    def execute_node(self, execution_id: str, node_id: str) -> Dict[str, Any]:
        try:
            execution = self._active_executions.get(execution_id)
            if not execution:
                return {"error": "Execution not found"}
            
            workflow = self._load_workflow(execution.workflow_id)
            node = next((n for n in workflow.nodes if n.node_id == node_id), None)
            
            if not node:
                return {"error": f"Node not found: {node_id}"}
            
            result = self._execute_node_logic(node, execution.context)
            
            if result.get("success"):
                execution.current_node = node.next_nodes[0] if node.next_nodes else workflow.exit_node
            else:
                execution.error_message = result.get("error")
                if node.retry_policy.get("max_retries", 0) > execution.retry_count:
                    execution.retry_count += 1
                    execution.current_node = node_id
                else:
                    execution.status = WorkflowStatus.FAILED.value
                    execution.completed_at = datetime.now().isoformat()
            
            self._save_execution(execution)
            return result
        except Exception as e:
            logger.error(f"Node execution failed: {e}")
            return {"error": str(e)}
    
    def _execute_node_logic(self, node: WorkflowNode, context: Dict[str, Any]) -> Dict[str, Any]:
        if node.type == WorkflowNodeType.VALIDATION.value:
            return self._validate_node(node, context)
        elif node.type == WorkflowNodeType.PUBLISH.value:
            return self._publish_node(node, context)
        elif node.type == WorkflowNodeType.NOTIFICATION.value:
            return self._notification_node(node, context)
        elif node.type == WorkflowNodeType.DECISION.value:
            return self._decision_node(node, context)
        return {"success": True}
    
    def _validate_node(self, node: WorkflowNode, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "validated": True}
    
    def _publish_node(self, node: WorkflowNode, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "published": True}
    
    def _notification_node(self, node: WorkflowNode, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "notified": True}
    
    def _decision_node(self, node: WorkflowNode, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "decision": "approved"}
    
    def _load_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM automation_workflows WHERE workflow_id = ?", (workflow_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return WorkflowDefinition(
                workflow_id=row["workflow_id"],
                name=row["name"],
                description=row.get("description", ""),
                version=row["version"],
                nodes=json.loads(row.get("nodes", "[]")),
                entry_node=row["entry_node"],
                exit_node=row["exit_node"],
                metadata=json.loads(row.get("metadata", "{}")),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
        except Exception as e:
            logger.error(f"Failed to load workflow: {e}")
            return None
    
    def _save_execution(self, execution: WorkflowExecution):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO workflow_executions 
                (execution_id, workflow_id, status, current_node, context, started_at,
                 completed_at, error_message, retry_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution.execution_id,
                execution.workflow_id,
                execution.status,
                execution.current_node,
                json.dumps(execution.context),
                execution.started_at,
                execution.completed_at,
                execution.error_message,
                execution.retry_count,
                execution.created_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save execution: {e}")


def main():
    print("Workflow Engine initialized")


if __name__ == "__main__":
    main()
