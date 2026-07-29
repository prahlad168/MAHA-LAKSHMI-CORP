#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - AI Provider Abstraction
Unified interface for multiple AI providers with fallback support.
"""

import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.marketing.ai")


class AIProviderType(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class AIMessage:
    """AI message structure"""
    role: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIResponse:
    """AI response structure"""
    content: str
    provider: str
    model: str
    tokens_used: int
    latency_ms: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    fallback_used: bool = False


@dataclass
class AIConfig:
    """AI provider configuration"""
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "default"
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 60
    retry_count: int = 3
    fallback_providers: List[str] = field(default_factory=list)


class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    PROVIDER_TYPE: AIProviderType = None
    DEFAULT_MODEL: str = "default"
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.provider_name = config.provider
        self.logger = logging.getLogger(f"maha-sales-engine.marketing.ai.{self.provider_name}")
    
    @abstractmethod
    async def generate(self, messages: List[AIMessage], **kwargs) -> AIResponse:
        """Generate response from AI"""
        pass
    
    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Check provider health"""
        pass
    
    def _build_response(self, content: str, model: str, tokens: int, latency: int, **kwargs) -> AIResponse:
        """Build standardized response"""
        return AIResponse(
            content=content,
            provider=self.provider_name,
            model=model,
            tokens_used=tokens,
            latency_ms=latency,
            metadata=kwargs
        )


class AIProviderManager:
    """Manage multiple AI providers with fallback"""
    
    def __init__(self):
        self._providers: Dict[str, BaseAIProvider] = {}
        self._provider_configs: Dict[str, AIConfig] = {}
        self._priority_order: List[str] = []
        self._default_provider: str = ""
    
    def register_provider(self, provider: BaseAIProvider, config: AIConfig, priority: int = 0):
        """Register AI provider"""
        self._providers[provider.provider_name] = provider
        self._provider_configs[provider.provider_name] = config
        self._priority_order.append(provider.provider_name)
        self._priority_order.sort(key=lambda x: -priority)
        logger.info(f"AI provider registered: {provider.provider_name}")
    
    def set_default(self, provider_name: str):
        """Set default provider"""
        if provider_name in self._providers:
            self._default_provider = provider_name
            logger.info(f"Default AI provider set: {provider_name}")
    
    async def generate(self, messages: List[AIMessage], provider: Optional[str] = None, **kwargs) -> AIResponse:
        """Generate with fallback support"""
        target_provider = provider or self._default_provider
        
        # Try primary provider
        if target_provider and target_provider in self._providers:
            try:
                response = await self._try_provider(target_provider, messages, **kwargs)
                if response:
                    return response
            except Exception as e:
                logger.warning(f"Primary provider {target_provider} failed: {e}")
        
        # Try fallback providers
        for fallback in self._get_fallback_order(target_provider):
            try:
                response = await self._try_provider(fallback, messages, **kwargs)
                if response:
                    response.fallback_used = True
                    logger.info(f"Fallback provider used: {fallback}")
                    return response
            except Exception as e:
                logger.warning(f"Fallback provider {fallback} failed: {e}")
        
        raise RuntimeError("All AI providers failed")
    
    def _get_fallback_order(self, exclude: Optional[str] = None) -> List[str]:
        """Get fallback provider order"""
        providers = [p for p in self._priority_order if p != exclude]
        return providers
    
    async def _try_provider(self, provider_name: str, messages: List[AIMessage], **kwargs) -> Optional[AIResponse]:
        """Try single provider with retry"""
        provider = self._providers.get(provider_name)
        config = self._provider_configs.get(provider_name)
        
        if not provider or not config:
            return None
        
        for attempt in range(config.retry_count):
            try:
                start_time = time.time()
                response = await provider.generate(messages, **kwargs)
                latency = int((time.time() - start_time) * 1000)
                response.latency_ms = latency
                return response
            except Exception as e:
                logger.warning(f"Provider {provider_name} attempt {attempt + 1} failed: {e}")
                if attempt < config.retry_count - 1:
                    await asyncio.sleep(2 ** attempt)
        
        return None
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self._providers.keys())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check all providers health"""
        results = {}
        for name, provider in self._providers.items():
            try:
                health = await provider.health()
                results[name] = health
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
        return results


def main():
    """Test AI provider manager"""
    manager = AIProviderManager()
    print("AI Provider Manager initialized")
    print(f"Available providers: {manager.get_available_providers()}")


if __name__ == "__main__":
    main()
