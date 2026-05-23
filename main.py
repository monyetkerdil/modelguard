"""
ModelGuard - Main Application
Entry point for the ML security platform.
"""

import asyncio
import argparse
import logging
from datetime import datetime

from core import ModelGuardEngine
from agents import (
    SentinelAgent, PoisonGuardAgent, ExtractionShieldAgent,
    PrivacyAgent, FairnessAgent, OrchestratorAgent
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("modelguard")


class ModelGuard:
    """Main ModelGuard application."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.engine = ModelGuardEngine()
        self._setup_agents()
    
    def _setup_agents(self):
        """Initialize all agents."""
        self.engine.register_agent("sentinel", SentinelAgent(self.engine, self.config.get("sentinel", {})))
        self.engine.register_agent("poison_guard", PoisonGuardAgent(self.engine, self.config.get("poison_guard", {})))
        self.engine.register_agent("extraction", ExtractionShieldAgent(self.engine, self.config.get("extraction", {})))
        self.engine.register_agent("privacy", PrivacyAgent(self.engine, self.config.get("privacy", {})))
        self.engine.register_agent("fairness", FairnessAgent(self.engine, self.config.get("fairness", {})))
        self.engine.register_agent("orchestrator", OrchestratorAgent(self.engine, self.config.get("orchestrator", {})))
        logger.info("All agents initialized")
    
    async def start(self, agents: list = None):
        """Start the platform."""
        logger.info("=" * 60)
        logger.info("ModelGuard - AI/ML Model Security Platform")
        logger.info("=" * 60)
        logger.info(f"Starting at {datetime.utcnow().isoformat()}")
        logger.info(f"Agents: {', '.join(self.engine.agents.keys())}")
        logger.info("=" * 60)
        await self.engine.start(agents)
    
    async def stop(self):
        """Stop the platform."""
        await self.engine.stop()
    
    def protect(self, model_id: str, model_type: str = "classifier", framework: str = "pytorch"):
        """Add model to protection."""
        self.engine.protect_model(model_id, model_type, framework)
    
    def status(self) -> dict:
        """Get platform status."""
        return self.engine.get_status()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="ModelGuard - AI/ML Model Security")
    parser.add_argument("action", choices=["start", "protect", "scan", "status"])
    parser.add_argument("--model", help="Model ID or path")
    parser.add_argument("--framework", default="pytorch", help="ML framework")
    parser.add_argument("--agents", nargs="+", help="Specific agents to run")
    
    args = parser.parse_args()
    platform = ModelGuard()
    
    if args.action == "start":
        try:
            if args.model:
                platform.protect(args.model, framework=args.framework)
            await platform.start(args.agents)
        except KeyboardInterrupt:
            pass
        finally:
            await platform.stop()
    
    elif args.action == "protect":
        if args.model:
            platform.protect(args.model, framework=args.framework)
            print(f"Protecting: {args.model}")
        else:
            print("Error: --model required")
    
    elif args.action == "scan":
        if args.model:
            print(f"Scanning {args.model}...")
        else:
            print("Error: --model required")
    
    elif args.action == "status":
        import json
        print(json.dumps(platform.status(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
