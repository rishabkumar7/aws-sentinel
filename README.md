
# AWS Sentinel

[![PyPI version](https://img.shields.io/pypi/v/aws-sentinel.svg)](https://pypi.org/project/aws-sentinel/)
[![GitHub stars](https://img.shields.io/github/stars/rishabkumar7/aws-sentinel.svg)](https://github.com/rishabkumar7/aws-sentinel/stargazers)
[![Downloads](https://static.pepy.tech/badge/aws-sentinel)](https://pepy.tech/project/aws-sentinel)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AWS Sentinel is a powerful command-line security scanner for AWS resources. It helps identify common security issues and misconfigurations in your AWS environment. Now featuring **natural language queries** powered by Amazon Bedrock!

```bash
 █████╗ ██╗    ██╗███████╗    ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     
██╔══██╗██║    ██║██╔════╝    ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     
███████║██║ █╗ ██║███████╗    ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     
██╔══██║██║███╗██║╚════██║    ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     
██║  ██║╚███╔███╔╝███████║    ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗
╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝    ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝
                                                                        
                      AWS Security Sentinel

Scanning AWS account using profile: default in region: us-east-1
Initializing security checks...
+-------------------------+
| AWS Security Issues Detected |
+--------+---------------+------------------------------------------+
| Service| Resource      | Issue                                    |
+--------+---------------+------------------------------------------+
| S3     | mybucket      | Public bucket                            |
| EC2    | sg-12345abcde | Security group with port 22 open to public |
| EBS    | vol-67890fghij| Unencrypted volume                       |
| IAM    | alice         | User without MFA                         |
+--------+---------------+------------------------------------------+
```

## Features

AWS Sentinel currently checks for the following security issues:

- **S3 Buckets**: Identifies publicly accessible buckets
- **EC2 Security Groups**: Finds security groups with port 22 (SSH) open to the public
- **EBS Volumes**: Detects unencrypted volumes
- **IAM Users**: Identifies users without Multi-Factor Authentication (MFA)

### 🆕 Natural Language Queries (Powered by Amazon Bedrock)

Ask security questions in plain English! AWS Sentinel now supports natural language queries using Amazon Bedrock's Nova Lite model.

**Examples:**
- "Are there any public S3 buckets?"
- "Check for high priority security issues"
- "Find IAM users without MFA"
- "Show me unencrypted storage volumes"

## Installation

You can install AWS Sentinel using pip:

```bash
pip install aws-sentinel
```

Or using uv

```bash
uv pip install aws-sentinel
```

## Usage

### Natural Language Queries 🆕

Ask security questions in plain English using Amazon Bedrock:

```bash
aws-sentinel ask "Are there any public S3 buckets?"
```

```bash
aws-sentinel ask "Check for high priority security issues"
```

```bash
aws-sentinel ask "Find IAM users without MFA"
```

**Natural Language Options:**
```
Usage: aws-sentinel ask [OPTIONS] QUERY

Options:
  --profile TEXT               AWS profile to use for authentication
  --region TEXT                AWS region to scan for security issues
  --bedrock-region TEXT        AWS region for Amazon Bedrock service
  --output [table|json|csv]    Output format for scan results
  -v, --verbose                Enable verbose output
  -h, --help                   Show this message and exit.
```

### Traditional Scanning

Run a full security scan using your default AWS profile:

```bash
aws-sentinel scan
```

If you don't specify a profile or region, it will use the default profile and `us-east-1` region.

### Command Options

```
Usage: aws-sentinel scan [OPTIONS]

Options:
  --profile TEXT               AWS profile to use for authentication (from
                               ~/.aws/credentials)
  --region TEXT                AWS region to scan for security issues
  --checks TEXT                Comma-separated list of checks to run
                               (s3,ec2,ebs,iam) or "all"
  --output [table|json|csv]    Output format for scan results
  --severity [low|medium|high|all]
                               Filter results by minimum severity level
  -v, --verbose                Enable verbose output
  -h, --help                   Show this message and exit.

```

### Examples

**Natural Language Queries:**

```bash
# Ask about specific services
aws-sentinel ask "Are there any public S3 buckets in my account?"

# Check for critical issues
aws-sentinel ask "What are the most critical security problems?"

# Filter by service type
aws-sentinel ask "Check IAM users for security issues"

# Export natural language results
aws-sentinel ask "Find all security issues" --output json > nl_security_report.json
```

**Traditional Scanning:**

Run a scan with a specific AWS profile and region:

```bash
aws-sentinel scan --profile production --region us-west-2
```

Run only specific security checks:

```bash
aws-sentinel scan --checks s3,iam
```

Export results in JSON format:

```bash
aws-sentinel scan --output json > security_report.json
```

Export results in CSV format:

```bash
aws-sentinel scan --output csv > security_report.csv
```

Show only high severity issues:

```bash
aws-sentinel scan --severity high
```

Get detailed documentation:

```bash
aws-sentinel docs
```

## Example Output

### Table Format (Default)

```bash
 █████╗ ██╗    ██╗███████╗    ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     
██╔══██╗██║    ██║██╔════╝    ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     
███████║██║ █╗ ██║███████╗    ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     
██╔══██║██║███╗██║╚════██║    ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     
██║  ██║╚███╔███╔╝███████║    ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗
╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝    ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝
                                                                        
                      AWS Security Sentinel

Scanning AWS account using profile: default in region: us-east-1
Initializing security checks...
+-------------------------+
| AWS Security Issues Detected |
+--------+---------------+------------------------------------------+
| Service| Resource      | Issue                                    |
+--------+---------------+------------------------------------------+
| S3     | mybucket      | Public bucket                            |
| EC2    | sg-12345abcde | Security group with port 22 open to public |
| EBS    | vol-67890fghij| Unencrypted volume                       |
| IAM    | alice         | User without MFA                         |
+--------+---------------+------------------------------------------+
```

### JSON Format

```json
{
  "scan_results": {
    "profile": "default",
    "region": "us-east-1",
    "scan_time": "2025-04-15T14:32:17.654321",
    "issues_count": 3,
    "issues": [
      {
        "service": "S3",
        "resource": "public-bucket",
        "issue": "Public bucket",
        "severity": "HIGH"
      },
      {
        "service": "EC2",
        "resource": "sg-12345abcde",
        "issue": "Security group with port 22 open to public",
        "severity": "HIGH"
      },
      {
        "service": "IAM",
        "resource": "admin-user",
        "issue": "User without MFA",
        "severity": "HIGH"
      }
    ]
  }
}

```

## Requirements

- Python 3.9+
- AWS credentials configured (via AWS CLI or environment variables)
- Required permissions to access AWS resources
- **For natural language queries**: Access to Amazon Bedrock with Nova Lite model

### Amazon Bedrock Setup

To use natural language queries, ensure you have:

1. **Access to Amazon Bedrock** in your AWS account
2. **Model access** to `amazon.nova-lite-v1:0`
3. **Appropriate IAM permissions** for Bedrock:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel"
         ],
         "Resource": "arn:aws:bedrock:*::foundation-model/amazon.nova-lite-v1:0"
       }
     ]
   }
   ```

**Note**: If Bedrock is unavailable, the tool automatically falls back to keyword-based parsing.

## Development

To set up the project for development:

1. Clone the repository:

    ```bash
    git clone https://github.com/rishabkumar7/aws-sentinel.git
    cd aws-sentinel
    
    ```

2. Create a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate    
    ```

3. Install development dependencies:

    ```bash
    pip install -e '.[dev]'
    ```

4. Run the tests:

    ```bash
    python -m unittest discover tests
    ```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit an Issue and a Pull Request.
