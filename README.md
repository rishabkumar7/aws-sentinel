
# AWS Sentinel

[![PyPI version](https://img.shields.io/pypi/v/aws-sentinel.svg)](https://pypi.org/project/aws-sentinel/)
[![GitHub stars](https://img.shields.io/github/stars/rishabkumar7/aws-sentinel.svg)](https://github.com/rishabkumar7/aws-sentinel/stargazers)
[![Downloads](https://static.pepy.tech/badge/aws-sentinel)](https://pepy.tech/project/aws-sentinel)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AWS Sentinel is a powerful command-line security scanner for AWS resources. It helps identify common security issues and misconfigurations in your AWS environment.

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

### Basic Usage

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
