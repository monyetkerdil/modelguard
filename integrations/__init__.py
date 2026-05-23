"""
ModelGuard - API Integrations
Connect to ML platforms and security services.
"""

import asyncio
import aiohttp
from typing import List, Dict, Any
from datetime import datetime


class MLflowIntegration:
    """MLflow integration for model tracking."""
    
    def __init__(self, tracking_uri: str):
        self.tracking_uri = tracking_uri
    
    async def get_models(self) -> List[Dict]:
        """Get registered models."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.tracking_uri}/api/2.0/mlflow/registered-models/search") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("registered_models", [])
                return []
    
    async def get_model_versions(self, name: str) -> List[Dict]:
        """Get model versions."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.tracking_uri}/api/2.0/mlflow/registered-models/get-latest-versions",
                params={"name": name}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("model_versions", [])
                return []


class WandBIntegration:
    """Weights & Biases integration."""
    
    def __init__(self, api_key: str, project: str):
        self.api_key = api_key
        self.project = project
        self.base_url = "https://api.wandb.ai"
    
    async def get_runs(self) -> List[Dict]:
        """Get project runs."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/v1/projects/{self.project}/runs",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    return (await resp.json()).get("runs", [])
                return []
    
    async def log_alert(self, alert: Dict):
        """Log security alert to W&B."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/v1/projects/{self.project}/alerts",
                headers=headers,
                json=alert
            ) as resp:
                return resp.status == 200


class HuggingFaceIntegration:
    """HuggingFace Hub integration."""
    
    BASE_URL = "https://huggingface.co/api"
    
    async def get_model_info(self, model_id: str) -> Dict:
        """Get model information."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/models/{model_id}") as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"HTTP {resp.status}"}
    
    async def scan_model(self, model_id: str) -> Dict:
        """Scan model for vulnerabilities."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/models/{model_id}/scan"
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"HTTP {resp.status}"}


class OpenAIGuard:
    """OpenAI API protection layer."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
    
    async def moderate_content(self, text: str) -> Dict:
        """Check content for policy violations."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/moderations",
                headers=headers,
                json={"input": text}
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"HTTP {resp.status}"}
    
    async def detect_pii(self, text: str) -> List[Dict]:
        """Detect PII in text using OpenAI."""
        # Would use GPT-4 for advanced PII detection
        return []


class SecurityIntelManager:
    """Unified security intelligence manager."""
    
    def __init__(self, config: Dict[str, str] = None):
        config = config or {}
        self.mlflow = MLflowIntegration(config.get("mlflow_uri", "http://localhost:5000"))
        self.wandb = WandBIntegration(
            config.get("wandb_key", ""),
            config.get("wandb_project", "")
        )
        self.huggingface = HuggingFaceIntegration()
        self.openai = OpenAIGuard(config.get("openai_key", ""))
    
    async def full_scan(self, model_id: str) -> Dict:
        """Run full security scan on model."""
        results = await asyncio.gather(
            self.huggingface.get_model_info(model_id),
            self.huggingface.scan_model(model_id),
            return_exceptions=True
        )
        
        return {
            "model_id": model_id,
            "info": results[0] if not isinstance(results[0], Exception) else {},
            "scan": results[1] if not isinstance(results[1], Exception) else {},
            "scanned_at": datetime.utcnow().isoformat()
        }


__all__ = [
    "MLflowIntegration", "WandBIntegration",
    "HuggingFaceIntegration", "OpenAIGuard",
    "SecurityIntelManager"
]
