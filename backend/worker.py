#!/usr/bin/env python3
"""
RQ Worker Script
Start this to process OCR jobs in the background

Usage:
    python worker.py
"""
import logging
from redis import Redis
from rq import Worker

from config import REDIS_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    # Create Redis connection
    redis_conn = Redis.from_url(REDIS_URL)
    
    # Create worker
    worker = Worker(['default'], connection=redis_conn)
    
    print("🚀 RQ Worker started. Waiting for jobs...")
    print(f"📡 Connected to Redis: {REDIS_URL}")
    print("Press Ctrl+C to stop")
    
    # Start processing jobs
    worker.work()
