"""
Test the natural language processing module
"""
import unittest
from unittest.mock import patch, MagicMock
import json
from aws_sentinel.nlp import BedrockNLPProcessor, process_natural_language_query


class TestBedrockNLPProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = BedrockNLPProcessor()
    
    def test_fallback_parse_s3_query(self):
        """Test fallback parsing for S3-related queries"""
        query = "Check my S3 buckets for security issues"
        result = self.processor._fallback_parse(query)
        
        self.assertIn('s3', result['services'])
        self.assertEqual(result['severity'], 'all')
        self.assertIn('s3', result['interpretation'].lower())
    
    def test_fallback_parse_high_severity(self):
        """Test fallback parsing for high severity queries"""
        query = "Find critical security problems"
        result = self.processor._fallback_parse(query)
        
        self.assertEqual(result['severity'], 'high')
        self.assertIn('high', result['interpretation'].lower())
    
    def test_fallback_parse_iam_query(self):
        """Test fallback parsing for IAM-related queries"""
        query = "Are there users without MFA?"
        result = self.processor._fallback_parse(query)
        
        self.assertIn('iam', result['services'])
    
    def test_fallback_parse_multiple_services(self):
        """Test fallback parsing for multiple services"""
        query = "Check S3 buckets and EC2 instances"
        result = self.processor._fallback_parse(query)
        
        self.assertIn('s3', result['services'])
        self.assertIn('ec2', result['services'])
    
    def test_fallback_parse_no_specific_service(self):
        """Test fallback parsing when no specific service is mentioned"""
        query = "Check for security issues"
        result = self.processor._fallback_parse(query)
        
        # Should default to all services
        expected_services = ['s3', 'ec2', 'ebs', 'iam']
        self.assertEqual(sorted(result['services']), sorted(expected_services))
    
    @patch('aws_sentinel.nlp.boto3.Session')
    def test_parse_query_with_bedrock_unavailable(self, mock_session):
        """Test parse_query when Bedrock is unavailable"""
        # Mock Bedrock client initialization to fail
        mock_session.return_value.client.side_effect = Exception("Bedrock unavailable")
        
        query = "Check S3 buckets"
        services, severity, interpretation = self.processor.parse_query(query)
        
        self.assertIn('s3', services)
        self.assertEqual(severity, 'all')
        self.assertIn('fallback', interpretation.lower())
    
    def test_create_bedrock_prompt(self):
        """Test that Bedrock prompt is properly formatted"""
        query = "Check S3 buckets"
        prompt = self.processor._create_bedrock_prompt(query)
        
        self.assertIn(query, prompt)
        self.assertIn('JSON', prompt)
        self.assertIn('services', prompt)
        self.assertIn('severity', prompt)


class TestProcessNaturalLanguageQuery(unittest.TestCase):
    
    @patch('aws_sentinel.nlp.BedrockNLPProcessor')
    def test_process_natural_language_query(self, mock_processor_class):
        """Test the main process_natural_language_query function"""
        mock_processor = MagicMock()
        mock_processor.parse_query.return_value = (['s3'], 'high', 'Test interpretation')
        mock_processor_class.return_value = mock_processor
        
        query = "Check S3 buckets for critical issues"
        services, severity, interpretation = process_natural_language_query(query)
        
        self.assertEqual(services, ['s3'])
        self.assertEqual(severity, 'high')
        self.assertEqual(interpretation, 'Test interpretation')


if __name__ == '__main__':
    unittest.main()