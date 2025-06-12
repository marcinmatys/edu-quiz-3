from fastapi import Request, Response, HTTPException, status
import time
from typing import Dict, List, Optional, Callable
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter implementation using token bucket algorithm"""
    
    def __init__(self, rate: float, per: float, burst: int = 1):
        """
        Initialize rate limiter
        
        Args:
            rate: Number of requests allowed per time period
            per: Time period in seconds
            burst: Maximum token bucket size (allows bursts of requests)
        """
        self.rate = rate
        self.per = per
        self.burst = burst
        self.tokens = burst
        self.updated_at = time.monotonic()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """
        Try to acquire a token
        
        Returns:
            True if token was acquired, False otherwise
        """
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.updated_at
            
            # Add tokens based on elapsed time
            self.tokens = min(
                self.burst,
                self.tokens + elapsed * (self.rate / self.per)
            )
            self.updated_at = now
            
            # Check if we have enough tokens
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            else:
                return False


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting specific endpoints"""
    
    def __init__(
        self,
        app,
        rate_limits: Dict[str, Dict[str, float]] = None
    ):
        """
        Initialize middleware
        
        Args:
            app: FastAPI application
            rate_limits: Dictionary mapping endpoint paths to rate limit settings
                Example: {
                    "/api/v1/quizzes": {"rate": 5, "per": 60, "burst": 10}
                }
        """
        super().__init__(app)
        self.rate_limiters: Dict[str, Dict[str, RateLimiter]] = {}
        
        # Configure rate limiters for paths
        if rate_limits:
            for path, limits in rate_limits.items():
                self.rate_limiters[path] = {}
                self.rate_limiters[path]["global"] = RateLimiter(
                    rate=limits.get("rate", 5),
                    per=limits.get("per", 60),
                    burst=limits.get("burst", 1)
                )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting"""
        # Check if path is rate limited
        path = request.url.path
        method = request.method
        
        # Only apply rate limiting to specific endpoints
        if method == "POST" and path in self.rate_limiters:
            # Try to get client IP for per-client rate limiting (future extension)
            client_ip = request.client.host if request.client else "unknown"
            
            # For now, we're just using global rate limiting
            limiter = self.rate_limiters[path]["global"]
            
            # Try to acquire a token
            if not await limiter.acquire():
                logger.warning(f"Rate limit exceeded for {path} from {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later."
                )
        
        # Process the request
        response = await call_next(request)
        return response 