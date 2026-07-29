#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Knowledge Graph
Represents relationships among products, customers, campaigns, marketplaces, licenses, orders, recommendations, policies, experiments, and revenue.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.knowledge.graph")


class NodeType(Enum):
    PRODUCT = "product"
    CUSTOMER = "customer"
    CAMPAIGN = "campaign"
    MARKETPLACE = "marketplace"
    LICENSE = "license"
    ORDER = "order"
    RECOMMENDATION = "recommendation"
    POLICY = "policy"
    EXPERIMENT = "experiment"
    REVENUE = "revenue"


class EdgeType(Enum):
    PURCHASED = "purchased"
    OPTIMIZED = "optimized"
    RECOMMENDED = "recommended"
    COMPLIED = "complied"
    TESTED = "tested"
    GENERATED = "generated"
    INFLUENCED = "influenced"
    RELATED = "related"


@dataclass
class GraphNode:
    node_id: str
    node_type: NodeType
    label: str
    properties: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class GraphEdge:
    edge_id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    properties: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class KnowledgeGraph:
    """
    Knowledge graph that represents relationships among entities.
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: List[GraphEdge] = []
    
    def add_node(self, node_type: NodeType, label: str, properties: Dict[str, Any]) -> GraphNode:
        """Add node to graph"""
        node_id = f"node-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        node = GraphNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            properties=properties
        )
        self._nodes[node_id] = node
        logger.info(f"Node added: {node_id} ({node_type.value})")
        return node
    
    def add_edge(self, source_id: str, target_id: str, edge_type: EdgeType, properties: Dict[str, Any] = None) -> GraphEdge:
        """Add edge to graph"""
        edge_id = f"edge-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        edge = GraphEdge(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            properties=properties or {}
        )
        self._edges.append(edge)
        logger.info(f"Edge added: {source_id} -> {target_id} ({edge_type.value})")
        return edge
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get node by ID"""
        return self._nodes.get(node_id)
    
    def get_edges(self, node_id: str) -> List[GraphEdge]:
        """Get edges connected to node"""
        return [e for e in self._edges if e.source_id == node_id or e.target_id == node_id]
    
    def find_path(self, source_id: str, target_id: str) -> Optional[List[GraphEdge]]:
        """Find path between nodes"""
        # Simple BFS
        visited = set()
        queue = [(source_id, [])]
        
        while queue:
            current, path = queue.pop(0)
            if current == target_id:
                return path
            
            if current in visited:
                continue
            visited.add(current)
            
            for edge in self.get_edges(current):
                if edge.source_id == current and edge.target_id not in visited:
                    queue.append((edge.target_id, path + [edge]))
        
        return None


def main():
    print("Knowledge Graph loaded")


if __name__ == "__main__":
    main()
