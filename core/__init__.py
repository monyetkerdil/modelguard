"""
ModelGuard - AI/ML Model Security Platform
Main engine coordinating 6 specialized agents.
"""

__version__ = "1.0.0"
__author__ = "ModelGuard Team"

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("modelguard")


class Severity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AttackType(Enum):
    """Types of ML attacks."""
    ADVERSARIAL = "adversarial"
    POISONING = "poisoning"
    EXTRACTION = "extraction"
    INVERSION = "inversion"
    MEMBERSHIP = "membership"
    BACKDOOR = "backdoor"


@dataclass
class SecurityAlert:
    """Represents a security alert."""
    id: str
    attack_type: AttackType
    severity: Severity
    title: str
    description: str
    model_id: str
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    mitigated: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "attack_type": self.attack_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "model_id": self.model_id,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "mitigated": self.mitigated
        }


@dataclass
class ModelMetrics:
    """Model security metrics."""
    models_protected: int = 0
    attacks_blocked: int = 0
    queries_analyzed: int = 0
    adversarial_detected: int = 0
    poisoning_attempts: int = 0
    extraction_attempts: int = 0
    privacy_violations: int = 0
    bias_alerts: int = 0


class ModelGuardEngine:
    """Core engine coordinating all security agents."""
    
    def __init__(self):
        self.agents: Dict[str, 'BaseAgent'] = {}
        self.alerts: List[SecurityAlert] = []
        self.metrics = ModelMetrics()
        self.running = False
        self._start_time = None
        self.protected_models: Dict[str, Dict] = {}
    
    def register_agent(self, name: str, agent: 'BaseAgent'):
        """Register a new agent."""
        self.agents[name] = agent
        logger.info(f"Agent registered: {name}")
    
    def protect_model(self, model_id: str, model_type: str, framework: str):
        """Add a model to protection."""
        self.protected_models[model_id] = {
            "type": model_type,
            "framework": framework,
            "added": datetime.utcnow().isoformat(),
            "queries": 0,
            "attacks_blocked": 0
        }
        self.metrics.models_protected += 1
        logger.info(f"Protecting model: {model_id}")
    
    async def start(self, agents: Optional[List[str]] = None):
        """Start all agents."""
        self.running = True
        self._start_time = datetime.utcnow()
        targets = agents or list(self.agents.keys())
        tasks = [self._run_agent(name) for name in targets if name in self.agents]
        logger.info(f"Starting {len(tasks)} agents...")
        await asyncio.gather(*tasks)
    
    async def _run_agent(self, name: str):
        """Run a single agent."""
        agent = self.agents[name]
        try:
            logger.info(f"Agent {name} started")
            await agent.run()
        except Exception as e:
            logger.error(f"Agent {name} error: {e}")
    
    async def stop(self):
        """Stop all agents."""
        self.running = False
        logger.info("All agents stopped")
    
    def add_alert(self, alert: SecurityAlert):
        """Add a security alert."""
        self.alerts.append(alert)
        self.metrics.attacks_blocked += 1
        logger.warning(f"Alert: {alert.title} [{alert.severity.value}]")
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            "running": self.running,
            "uptime": (datetime.utcnow() - self._start_time).total_seconds() if self._start_time else 0,
            "protected_models": len(self.protected_models),
            "total_alerts": len(self.alerts),
            "attacks_blocked": self.metrics.attacks_blocked,
            "agents": {
                name: {"status": "active"}
                for name in self.agents
            }
        }


class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, name: str, engine: ModelGuardEngine):
        self.name = name
        self.engine = engine
    
    async def run(self):
        """Main agent loop."""
        while self.engine.running:
            await self.process()
            await asyncio.sleep(1)
    
    async def process(self):
        """Process events. Override in subclass."""
        raise NotImplementedError
    
    def report_alert(self, alert: SecurityAlert):
        """Report an alert."""
        self.engine.add_alert(alert)


__all__ = [
    "ModelGuardEngine", "BaseAgent", "SecurityAlert",
    "Severity", "AttackType", "ModelMetrics"
]
