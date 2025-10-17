# Prerequisites

Before starting, ensure you have:
* Git
* Python 
* Node.js and npm
* AWS CLI 
* AWS CDK
* AWS credentials

# Steps to deploy:

1. Clone the Repository:
```
git clone https://github.com/DacheOA/Technical_Challenge_Stori.git
cd Technical_Challenge_Stori

```

2. Create and activate a virtual environment:
```
python -m venv .env
source .env/bin/activate     # Linux/MacOS
.\.env\Scripts\activate      # Windows

```

3. Install dependencies:
```
pip install -r requirements.txt     

```

4. Bootstrap your environment:
```
npx cdk bootstrap aws://<your-account-id>/<your-region>   

```

5. Generate the CloudFormation template from the CDK app:
```
cdk synth 

```

6. Deply Infrastructure:
```
cdk deploy 

```

# Usage:
Upload a CSV file and the flow will start
```
aws s3 cp challenge_100_transactions.csv s3://<your-bucket-name>/challenge_100_transactions.csv 

```

# Query the API
AWS
1. Find your API Gateway URL in the AWS Console or output during deployment

2. Make GET requests:
```
curl https://<api-id>.execute-api.<region>.amazonaws.com/dev/user/1 --- curl https://4w2l14kx54.execute-api.us-east-2.amazonaws.com/dev/user/1

curl https://<api-id>.execute-api.<region>.amazonaws.com/dev/user/1?min_amount=50

```

Locally
1. Install dependencies:
```
pip install -r requirements-dev.txt     

```

2. Install dependencies:
```
uvicorn api.main:app --reload

```

3. Make GET requests:
```
curl http://127.0.0.1:8000/user/1

curl http://127.0.0.1:8000/user/1?min_amount=50

```

# Run Unit Tests
1. Install dependencies:
```
pip install -r requirements-test.txt     

```

2. Run Unit Tests:
```
pytest 

```

# Clean Up
To delete all resources:
```
cdk destroy    

```