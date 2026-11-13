#!/usr/bin/env python3
"""Test Gemini API directly"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jarvis'))

async def test_gemini():
    from jarvis.config import Config
    from jarvis.llm.gemini import GeminiLLM
    
    print("=" * 70)
    print("Testing Gemini API Direct Connection")
    print("=" * 70)
    
    cfg = Config.load()
    print(f"\n✓ Config loaded")
    print(f"  Model: {cfg.planner_model}")
    
    # Check API key
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if api_key:
        print(f"  API Key: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("  ✗ No API key found!")
        return
    
    # Create LLM
    print(f"\n✓ Creating GeminiLLM...")
    try:
        llm = GeminiLLM(cfg.planner_model)
        print(f"  Model: {llm.model}")
        print(f"  API Key configured: {bool(llm.api_key)}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return
    
    # Test simple completion
    print(f"\n✓ Testing simple completion...")
    try:
        schema = {"type": "object", "properties": {"answer": {"type": "string"}}}
        data, usage = await llm.complete_json(
            "You are a helpful assistant.",
            [{"role": "user", "content": "Say 'Hello from Gemini!'"}],
            schema,
            thinking="low"
        )
        print(f"  Response: {data}")
        print(f"  Model used: {usage.model}")
        print(f"  Tokens: {usage.input_tokens + usage.output_tokens}")
    except Exception as e:
        print(f"  ✗ API call failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 70)
    print("✓ Gemini API is working!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_gemini())
