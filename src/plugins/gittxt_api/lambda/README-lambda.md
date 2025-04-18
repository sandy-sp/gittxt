# 🧪 Deploy Gittxt API to AWS Lambda

## Prereqs
- AWS CLI
- AWS SAM CLI
- Python 3.12
- Docker (for building)

## Deploy

```bash
cd plugins/gittxt_api/lambda
sam build
sam deploy --guided
```
