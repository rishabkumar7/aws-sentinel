"""
Natural Language Processing module for AWS Sentinel using Amazon Bedrock Nova Lite
"""
import json
import boto3
from botocore.exceptions import ClientError
import re
from typing import Dict, List, Tuple, Optional


class BedrockNLPProcessor:
    """
    Natural Language Processor using Amazon Bedrock Nova Lite to convert user queries
    into structured security scan parameters.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """
        Initialize the Bedrock NLP processor.
        
        Args:
            region: AWS region for Bedrock service
        """
        self.region = region
        self.bedrock_client = None
        self.model_id = "amazon.nova-lite-v1:0"
        
        # Mapping of natural language terms to our security checks
        self.service_mappings = {
            's3': ['s3', 'bucket', 'buckets', 'storage', 'object storage'],
            'ec2': ['ec2', 'instance', 'instances', 'virtual machine', 'vm', 'compute', 'security group', 'security groups'],
            'ebs': ['ebs', 'volume', 'volumes', 'disk', 'storage volume', 'block storage'],
            'iam': ['iam', 'user', 'users', 'identity', 'access', 'authentication', 'mfa', 'multi-factor']
        }
        
        self.severity_mappings = {
            'high': ['high', 'critical', 'severe', 'urgent', 'important'],
            'medium': ['medium', 'moderate', 'normal'],
            'low': ['low', 'minor', 'informational']
        }
    
    def _initialize_bedrock_client(self, profile: str = 'default') -> bool:
        """
        Initialize the Bedrock client.
        
        Args:
            profile: AWS profile to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            session = boto3.Session(profile_name=profile)
            self.bedrock_client = session.client('bedrock-runtime', region_name=self.region)
            return True
        except Exception as e:
            print(f"Error initializing Bedrock client: {str(e)}")
            return False
    
    def _create_bedrock_prompt(self, user_query: str) -> str:
        """
        Create a structured prompt for Bedrock to parse the user's natural language query.
        
        Args:
            user_query: The user's natural language security query
            
        Returns:
            str: Formatted prompt for Bedrock
        """
        prompt = f"""
You are an AWS security expert helping users translate natural language queries into structured security scan parameters.

Parse the following user query and extract security scan parameters:

User Query: "{user_query}"

Available AWS services to scan:
- s3: Check for public S3 buckets
- ec2: Check for security groups with SSH access open to public
- ebs: Check for unencrypted EBS volumes  
- iam: Check for IAM users without MFA

Available severity levels: high, medium, low, all

Output your response as valid JSON with this exact structure:
{{
    "services": ["s3", "ec2", "ebs", "iam"],
    "severity": "all",
    "interpretation": "Brief explanation of what you understood from the query"
}}

Rules:
1. If the user mentions specific services, only include those in the services array
2. If no services are mentioned, include all: ["s3", "ec2", "ebs", "iam"]
3. If severity is mentioned, set it accordingly, otherwise use "all"
4. Always provide a brief interpretation

Examples:
- "Check S3 buckets for security issues" -> {{"services": ["s3"], "severity": "all", "interpretation": "Scanning S3 buckets for public access issues"}}
- "Find high priority security problems" -> {{"services": ["s3", "ec2", "ebs", "iam"], "severity": "high", "interpretation": "Scanning all services for high severity security issues"}}
- "Are there any IAM users without MFA?" -> {{"services": ["iam"], "severity": "all", "interpretation": "Checking IAM users for missing multi-factor authentication"}}

Parse this query now and respond with only the JSON:
"""
        return prompt
    
    def _call_bedrock_model(self, prompt: str) -> Optional[Dict]:
        """
        Call the Bedrock model with the given prompt.
        
        Args:
            prompt: The prompt to send to Bedrock
            
        Returns:
            Dict: Parsed response from Bedrock, or None if error
        """
        try:
            # Amazon Nova model request format
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
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract content from Amazon Nova response format
            if 'output' in response_body and 'message' in response_body['output']:
                content = response_body['output']['message']['content'][0]['text']
            else:
                print(f"Unexpected Nova response format: {response_body}")
                return None
            
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                print(f"Could not extract JSON from Bedrock response: {content}")
                return None
                
        except ClientError as e:
            print(f"Error calling Bedrock: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing Bedrock response: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error with Bedrock: {str(e)}")
            return None
    
    def _fallback_parse(self, user_query: str) -> Dict:
        """
        Fallback parsing using simple keyword matching if Bedrock is unavailable.
        
        Args:
            user_query: The user's natural language query
            
        Returns:
            Dict: Parsed scan parameters
        """
        query_lower = user_query.lower()
        
        # Determine services
        services = []
        for service, keywords in self.service_mappings.items():
            if any(keyword in query_lower for keyword in keywords):
                services.append(service)
        
        # If no specific services found, scan all
        if not services:
            services = ['s3', 'ec2', 'ebs', 'iam']
        
        # Determine severity
        severity = 'all'
        for sev_level, keywords in self.severity_mappings.items():
            if any(keyword in query_lower for keyword in keywords):
                severity = sev_level
                break
        
        return {
            'services': services,
            'severity': severity,
            'interpretation': f"Fallback parsing: Scanning {', '.join(services)} services with {severity} severity filter"
        }
    
    def parse_query(self, user_query: str, profile: str = 'default') -> Tuple[List[str], str, str]:
        """
        Parse a natural language security query into structured parameters.
        
        Args:
            user_query: The user's natural language query
            profile: AWS profile to use for Bedrock
            
        Returns:
            Tuple: (services_list, severity_level, interpretation)
        """
        # Try to use Bedrock first
        if self._initialize_bedrock_client(profile):
            prompt = self._create_bedrock_prompt(user_query)
            bedrock_result = self._call_bedrock_model(prompt)
            
            if bedrock_result:
                services = bedrock_result.get('services', ['s3', 'ec2', 'ebs', 'iam'])
                severity = bedrock_result.get('severity', 'all')
                interpretation = bedrock_result.get('interpretation', 'Bedrock parsing successful')
                return services, severity, interpretation
        
        # Fallback to simple keyword matching
        print("Using fallback parsing (Bedrock unavailable)")
        fallback_result = self._fallback_parse(user_query)
        return (
            fallback_result['services'],
            fallback_result['severity'],
            fallback_result['interpretation']
        )


def process_natural_language_query(query: str, profile: str = 'default', region: str = 'us-east-1') -> Tuple[List[str], str, str]:
    """
    Process a natural language security query and return scan parameters.
    
    Args:
        query: Natural language query from user
        profile: AWS profile to use
        region: AWS region for Bedrock
        
    Returns:
        Tuple: (services_to_scan, severity_filter, interpretation)
    """
    processor = BedrockNLPProcessor(region=region)
    return processor.parse_query(query, profile)