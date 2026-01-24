#!/usr/bin/env python3
"""
Quick test to validate CLI structure
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from aws_sentinel.cli import main
    from aws_sentinel.nlp import BedrockNLPProcessor, process_natural_language_query
    
    print("✅ All imports successful!")
    print("✅ CLI module loads correctly")
    print("✅ NLP module with Amazon Nova loads correctly")
    
    # Test the processor initialization
    processor = BedrockNLPProcessor()
    print(f"✅ BedrockNLPProcessor initialized with model: {processor.model_id}")
    
    # Test a simple query without calling Bedrock
    services, severity, interpretation = process_natural_language_query(
        "Check S3 buckets", profile="default", region="us-east-1"
    )
    print(f"✅ Natural language processing works:")
    print(f"   Services: {services}")
    print(f"   Severity: {severity}")
    print(f"   Interpretation: {interpretation}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nIntegration test completed!")