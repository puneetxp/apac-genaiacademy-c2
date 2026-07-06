"""
Test script for Google Antigravity Agent migration.
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.orchestrator_agent import run_orchestrator_turn

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def main():
    print("====================================================")
    print("Testing Google Antigravity Root Orchestrator Agent...")
    print("====================================================")
    
    # We will test in mock mode since no credentials are provided yet
    query = "What crops are recommended for clay soil and drip irrigation in summer? Let's check weather forecast too."
    print(f"User Query: {query}\n")
    
    response = await run_orchestrator_turn(query=query, farm_id=None)
    
    print("\n================== Response ==================")
    print(response)
    print("================================================")

if __name__ == "__main__":
    asyncio.run(main())
