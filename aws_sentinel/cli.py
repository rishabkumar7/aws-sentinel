"""
CLI interface for AWS Sentinel
"""
import boto3
import click
import sys
import json
from datetime import datetime
from .utils import import_datetime_for_json
from .core import (
    check_public_buckets,
    check_public_security_groups,
    check_unencrypted_ebs_volumes,
    check_iam_users_without_mfa
)
from .utils import create_pretty_table
from .ascii_art import BANNER
from .nlp import process_natural_language_query

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(
    version='0.1.1', 
    prog_name='AWS Sentinel',
    message='%(prog)s v%(version)s - A security scanner for AWS resources'
)
def main():
    """
    \b
     █████╗ ██╗    ██╗███████╗    ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     
    ██╔══██╗██║    ██║██╔════╝    ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     
    ███████║██║ █╗ ██║███████╗    ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     
    ██╔══██║██║███╗██║╚════██║    ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     
    ██║  ██║╚███╔███╔╝███████║    ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗
    ╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝    ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝
    
                        AWS Security Sentinel
    
    Scans your AWS account for security vulnerabilities and misconfigurations.
    
    Commands:
      scan    Run a security scan on your AWS resources
      ask     Ask a natural language security question (powered by Amazon Bedrock)
      
    Examples:
      aws-sentinel scan --profile production --region us-west-2
      aws-sentinel scan --checks s3,ec2 --output json
      aws-sentinel ask "Are there any public S3 buckets?"
      aws-sentinel ask "Check for high priority security issues"
    """
    pass

@main.command('scan')
@click.option('--profile', default='default', 
              help='AWS profile to use for authentication (from ~/.aws/credentials)')
@click.option('--region', default='us-east-1', 
              help='AWS region to scan for security issues')
@click.option('--checks', default='all',
              help='Comma-separated list of checks to run (s3,ec2,ebs,iam) or "all"')
@click.option('--output', type=click.Choice(['table', 'json', 'csv']), default='table',
              help='Output format for scan results')
@click.option('--severity', type=click.Choice(['low', 'medium', 'high', 'all']), default='all',
              help='Filter results by minimum severity level')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def scan(profile, region, checks, output, severity, verbose):
    """
    Run a comprehensive security scan on your AWS resources.
    
    This command analyzes your AWS account for various security issues,
    including public S3 buckets, exposed security groups, unencrypted
    volumes, and IAM users without MFA.
    """
    if output == 'table':
        print(BANNER)
        click.echo(f"Scanning AWS account using profile: {profile} in region: {region}")
    if verbose:
        click.echo(f"Checks: {checks}")
        click.echo(f"Output format: {output}")
        click.echo(f"Severity filter: {severity}")
    
    if output == 'table':
        click.echo("Initializing security checks...\n")

    try:
        session = boto3.Session(profile_name=profile, region_name=region)
        s3_client = session.client('s3')
        ec2_client = session.client('ec2')
        iam_client = session.client('iam')
    except Exception as e:
        click.echo(f"Error connecting to AWS: {str(e)}", err=True)
        sys.exit(1)

    results = []
    checks_to_run = checks.lower().split(',') if checks.lower() != 'all' else ['s3', 'ec2', 'ebs', 'iam']
    
    if verbose:
        click.echo(f"Starting scan with the following checks: {', '.join(checks_to_run)}")
    
    # S3 Buckets Check
    if 's3' in checks_to_run:
        if verbose:
            click.echo("Checking for public S3 buckets...")
        public_buckets = check_public_buckets(s3_client)
        for bucket in public_buckets:
            results.append(["S3", bucket, "Public bucket", "HIGH"])
    
    # Security Groups Check
    if 'ec2' in checks_to_run:
        if verbose:
            click.echo("Checking for security groups with public access...")
        public_sgs = check_public_security_groups(ec2_client)
        for sg in public_sgs:
            results.append(["EC2", sg, "Security group with port 22 open to public", "HIGH"])
    
    # EBS Volumes Check
    if 'ebs' in checks_to_run:
        if verbose:
            click.echo("Checking for unencrypted EBS volumes...")
        unencrypted_volumes = check_unencrypted_ebs_volumes(ec2_client)
        for volume in unencrypted_volumes:
            results.append(["EBS", volume, "Unencrypted volume", "MEDIUM"])
    
    # IAM Users Check
    if 'iam' in checks_to_run:
        if verbose:
            click.echo("Checking for IAM users without MFA...")
        users_without_mfa = check_iam_users_without_mfa(iam_client)
        for user in users_without_mfa:
            results.append(["IAM", user, "User without MFA", "HIGH"])

    # Filter by severity if needed
    if severity != 'all':
        severity_levels = {
            'low': ['LOW', 'MEDIUM', 'HIGH'],
            'medium': ['MEDIUM', 'HIGH'],
            'high': ['HIGH']
        }
        results = [r for r in results if r[3] in severity_levels[severity]]
    
    # Output results
    if results:
        if output == 'table':
            table = create_pretty_table(
                "AWS Security Issues Detected",
                ["Service", "Resource", "Issue", "Severity"],
                results
            )
            print(table)
            click.echo(f"\nScan complete. Found {len(results)} security issues.")
        elif output == 'json':
            import json
            json_results = {
                'scan_results': {
                    'profile': profile,
                    'region': region,
                    'scan_time': import_datetime_for_json(),
                    'issues_count': len(results),
                    'issues': []
                }
            }
            
            for r in results:
                json_results['scan_results']['issues'].append({
                    'service': r[0],
                    'resource': r[1],
                    'issue': r[2],
                    'severity': r[3]
                })
            
            # Only output the JSON with no additional text
            print(json.dumps(json_results, indent=2, sort_keys=False, ensure_ascii=False))
        elif output == 'csv':
            import csv
            from io import StringIO
            output_buffer = StringIO()
            writer = csv.writer(output_buffer)
            writer.writerow(["Service", "Resource", "Issue", "Severity"])
            writer.writerows(results)
            # Only output the CSV with no additional text
            print(output_buffer.getvalue().strip())
    else:
        if output == 'table':
            click.echo("No security issues found. Your AWS environment looks secure!")
        elif output == 'json':
            empty_result = {
                'scan_results': {
                    'profile': profile,
                    'region': region,
                    'scan_time': import_datetime_for_json(),
                    'issues_count': 0,
                    'issues': []
                }
            }
            print(json.dumps(empty_result, indent=2, sort_keys=False, ensure_ascii=False))
        elif output == 'csv':
            print("Service,Resource,Issue,Severity")

@main.command('ask')
@click.argument('query')
@click.option('--profile', default='default', 
              help='AWS profile to use for authentication (from ~/.aws/credentials)')
@click.option('--region', default='us-east-1', 
              help='AWS region to scan for security issues')
@click.option('--bedrock-region', default='us-east-1',
              help='AWS region for Amazon Bedrock service (default: us-east-1)')
@click.option('--output', type=click.Choice(['table', 'json', 'csv']), default='table',
              help='Output format for scan results')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def ask(query, profile, region, bedrock_region, output, verbose):
    """
    Ask a natural language security question about your AWS resources.
    
    This command uses Amazon Bedrock's Nova Lite model to understand your natural language query
    and automatically determines which security checks to run.
    
    Examples:
    \b
      aws-sentinel ask "Are there any public S3 buckets?"
      aws-sentinel ask "Check for high priority security issues"
      aws-sentinel ask "Find IAM users without MFA"
      aws-sentinel ask "Show me unencrypted storage volumes"
    """
    if output == 'table':
        print(BANNER)
        click.echo(f"Processing natural language query: '{query}'")
        click.echo(f"Using AWS profile: {profile} in region: {region}")
        if bedrock_region != region:
            click.echo(f"Using Bedrock in region: {bedrock_region}")
    
    if verbose:
        click.echo(f"Output format: {output}")
        click.echo(f"Verbose mode enabled")
    
    # Process the natural language query
    try:
        services_to_scan, severity_filter, interpretation = process_natural_language_query(
            query, profile, bedrock_region
        )
        
        if output == 'table':
            click.echo(f"Interpretation: {interpretation}")
            click.echo(f"Services to scan: {', '.join(services_to_scan)}")
            click.echo(f"Severity filter: {severity_filter}")
            click.echo("Initializing security checks...\n")
        
        if verbose:
            click.echo(f"Parsed services: {services_to_scan}")
            click.echo(f"Parsed severity: {severity_filter}")
            
    except Exception as e:
        click.echo(f"Error processing natural language query: {str(e)}", err=True)
        sys.exit(1)

    # Set up AWS clients
    try:
        session = boto3.Session(profile_name=profile, region_name=region)
        s3_client = session.client('s3')
        ec2_client = session.client('ec2')
        iam_client = session.client('iam')
    except Exception as e:
        click.echo(f"Error connecting to AWS: {str(e)}", err=True)
        sys.exit(1)

    results = []
    
    if verbose:
        click.echo(f"Starting scan with the following checks: {', '.join(services_to_scan)}")
    
    # S3 Buckets Check
    if 's3' in services_to_scan:
        if verbose:
            click.echo("Checking for public S3 buckets...")
        public_buckets = check_public_buckets(s3_client)
        for bucket in public_buckets:
            results.append(["S3", bucket, "Public bucket", "HIGH"])
    
    # Security Groups Check
    if 'ec2' in services_to_scan:
        if verbose:
            click.echo("Checking for security groups with public access...")
        public_sgs = check_public_security_groups(ec2_client)
        for sg in public_sgs:
            results.append(["EC2", sg, "Security group with port 22 open to public", "HIGH"])
    
    # EBS Volumes Check
    if 'ebs' in services_to_scan:
        if verbose:
            click.echo("Checking for unencrypted EBS volumes...")
        unencrypted_volumes = check_unencrypted_ebs_volumes(ec2_client)
        for volume in unencrypted_volumes:
            results.append(["EBS", volume, "Unencrypted volume", "MEDIUM"])
    
    # IAM Users Check
    if 'iam' in services_to_scan:
        if verbose:
            click.echo("Checking for IAM users without MFA...")
        users_without_mfa = check_iam_users_without_mfa(iam_client)
        for user in users_without_mfa:
            results.append(["IAM", user, "User without MFA", "HIGH"])

    # Filter by severity if needed
    if severity_filter != 'all':
        severity_levels = {
            'low': ['LOW', 'MEDIUM', 'HIGH'],
            'medium': ['MEDIUM', 'HIGH'],
            'high': ['HIGH']
        }
        results = [r for r in results if r[3] in severity_levels[severity_filter]]
    
    # Output results
    if results:
        if output == 'table':
            table = create_pretty_table(
                "AWS Security Issues Detected",
                ["Service", "Resource", "Issue", "Severity"],
                results
            )
            print(table)
            click.echo(f"\nScan complete. Found {len(results)} security issues.")
        elif output == 'json':
            import json
            json_results = {
                'scan_results': {
                    'profile': profile,
                    'region': region,
                    'query': query,
                    'interpretation': interpretation,
                    'services_scanned': services_to_scan,
                    'severity_filter': severity_filter,
                    'scan_time': import_datetime_for_json(),
                    'issues_count': len(results),
                    'issues': []
                }
            }
            
            for r in results:
                json_results['scan_results']['issues'].append({
                    'service': r[0],
                    'resource': r[1],
                    'issue': r[2],
                    'severity': r[3]
                })
            
            # Only output the JSON with no additional text
            print(json.dumps(json_results, indent=2, sort_keys=False, ensure_ascii=False))
        elif output == 'csv':
            import csv
            from io import StringIO
            output_buffer = StringIO()
            writer = csv.writer(output_buffer)
            writer.writerow(["Service", "Resource", "Issue", "Severity"])
            writer.writerows(results)
            # Only output the CSV with no additional text
            print(output_buffer.getvalue().strip())
    else:
        if output == 'table':
            click.echo(f"No security issues found matching your query. Your AWS environment looks secure!")
        elif output == 'json':
            empty_result = {
                'scan_results': {
                    'profile': profile,
                    'region': region,
                    'query': query,
                    'interpretation': interpretation,
                    'services_scanned': services_to_scan,
                    'severity_filter': severity_filter,
                    'scan_time': import_datetime_for_json(),
                    'issues_count': 0,
                    'issues': []
                }
            }
            print(json.dumps(empty_result, indent=2, sort_keys=False, ensure_ascii=False))
        elif output == 'csv':
            print("Service,Resource,Issue,Severity")

@main.command('version')
def version():
    """Display the version of AWS Sentinel."""
    click.echo("AWS Sentinel v0.1.1")

# Add a docs command to show more detailed usage instructions
@main.command('docs')
def docs():
    """Display detailed documentation about AWS Sentinel."""
    doc_text = """
    AWS Sentinel Documentation
    =========================
    
    DESCRIPTION
    -----------
    AWS Sentinel is a security scanner for AWS resources that helps identify common
    security issues and misconfigurations in your AWS account. It supports both
    traditional command-line scanning and natural language queries powered by Amazon Bedrock.
    
    SUPPORTED CHECKS
    ---------------
    * S3: Public bucket access
    * EC2: Security groups with SSH (port 22) open to the world
    * EBS: Unencrypted volumes
    * IAM: Users without Multi-Factor Authentication (MFA)
    
    COMMANDS
    --------
    scan    - Run structured security scans with specific parameters
    ask     - Ask natural language security questions (requires Amazon Bedrock Nova Lite)
    
    PREREQUISITES
    ------------
    1. AWS CLI configured with appropriate credentials
    2. Required permissions to access resources in your AWS account
    3. For natural language queries: Access to Amazon Bedrock (Nova Lite model)
    
    EXAMPLES
    --------
    # Traditional scanning
    aws-sentinel scan
    aws-sentinel scan --profile production --region us-west-2
    aws-sentinel scan --checks s3,iam
    aws-sentinel scan --output json > security_report.json
    aws-sentinel scan --severity high
    aws-sentinel scan -v
    
    # Natural language queries (powered by Amazon Bedrock)
    aws-sentinel ask "Are there any public S3 buckets?"
    aws-sentinel ask "Check for high priority security issues"
    aws-sentinel ask "Find IAM users without MFA"
    aws-sentinel ask "Show me unencrypted storage volumes"
    aws-sentinel ask "What security problems do I have?" --output json
    
    NATURAL LANGUAGE EXAMPLES
    ------------------------
    * "Check S3 buckets for security issues"
    * "Find high priority security problems"
    * "Are there IAM users without multi-factor authentication?"
    * "Show me all unencrypted volumes"
    * "What are the most critical security issues?"
    * "Check everything for security problems"
    """
    click.echo(doc_text)

if __name__ == '__main__':
    main()