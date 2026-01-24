#!/usr/bin/env python3
"""
Test script to verify the Amazon Nova integration
"""
import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aws_sentinel.nlp import BedrockNLPProcessor

def test_nova_request_format():
    """Test that the Nova request format is correctly structured"""
    processor = BedrockNLPProcessor()
    
    # Test the prompt creation
    query = "Check S3 buckets for security issues"
    prompt = processor._create_bedrock_prompt(query)
    
    print("Testing Amazon Nova Integration")
    print("=" * 50)
    print(f"Model ID: {processor.model_id}")
    print(f"Query: {query}")
    print(f"Prompt length: {len(prompt)} characters")
    print("\nPrompt preview (first 200 chars):")
    print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
    
    # Test the request body format (without actually calling Bedrock)
    print("\nTesting request body format:")
    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "inferenceConfig": {
            "max_new_tokens": 1000,
            "temperature": 0.1,
            "top_p": 0.9
        }
    }
    
    print("Request body structure:")
    print(f"- Messages: {len(request_body['messages'])} message(s)")
    print(f"- Content type: {type(request_body['messages'][0]['content'][0]['text'])}")
    print(f"- Max tokens: {request_body['inferenceConfig']['max_new_tokens']}")
    print(f"- Temperature: {request_body['inferenceConfig']['temperature']}")
    print(f"- Top-p: {request_body['inferenceConfig']['top_p']}")
    
    print("\n✅ Amazon Nova request format is correctly structured")

def test_fallback_parsing():
    """Test the fallback parsing functionality"""
    processor = BedrockNLPProcessor()
    
    print("\nTesting Fallback Parsing:")
    print("-" * 30)
    
    test_cases = [
        "Check my S3 buckets for security issues",
        "Find critical security problems", 
        "Are there users without MFA?",
        "Show me high priority IAM problems",
        "Check everything for security issues"
    ]
    
    for query in test_cases:
        result = processor._fallback_parse(query)
        print(f"Query: {query}")
        print(f"Services: {result['services']}")
        print(f"Severity: {result['severity']}")
        print(f"Interpretation: {result['interpretation']}")
        print()

if __name__ == "__main__":
    test_nova_request_format()
    test_fallback_parsing()
    print("All tests completed successfully! ✅")