# User management backend
The project implements a *user management backend* component that uses 
Amazon API Gateway, AWS Lambda and Amazon DynamoDB to provide basic 
CRUD operations for managing users. The project also includes a continuous 
deployment pipeline.

![diagram](https://user-images.githubusercontent.com/4362270/129941071-263c1d8f-0357-4dec-80e1-e308048abaff.png)
\* Diagram generated using https://github.com/pistazie/cdk-dia

## Create a new repository from usermanagement-backend
This is optional for deploying the component to the development environment, but 
**required** for deploying the pipeline.

The instructions below use the usermanagement-backend repository.

## Create development environment
See [Getting Started With the AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
for additional details and prerequisites

### Clone the code
```bash
git clone https://github.com/alexpulver/usermanagement-backend
cd usermanagement-backend
```

### Create Python virtual environment and install the dependencies
```bash
python3.7 -m venv .venv
source .venv/bin/activate
# [Optional] Needed to upgrade dependencies and cleanup unused packages
pip install pip-tools==6.1.0
./scripts/install-deps.sh
./scripts/run-tests.sh
```

### [Optional] Upgrade AWS CDK Toolkit version
**Note:** If you are planning to upgrade dependencies, first push the upgraded AWS CDK Toolkit version.
See [(pipelines): Fail synth if pinned CDK CLI version is older than CDK library version](https://github.com/aws/aws-cdk/issues/15519) 
for more details.

```bash
vi package.json  # Update "aws-cdk" package version
./scripts/install-deps.sh
./scripts/run-tests.sh
```

### [Optional] Upgrade dependencies (ordered by constraints)
Consider [AWS CDK Toolkit (CLI)](https://docs.aws.amazon.com/cdk/latest/guide/reference.html#versioning) compatibility 
when upgrading AWS CDK packages version.

```bash
pip-compile --upgrade api/runtime/requirements.in
pip-compile --upgrade requirements.in
pip-compile --upgrade requirements-dev.in
./scripts/install-deps.sh
# [Optional] Cleanup unused packages
pip-sync api/runtime/requirements.txt requirements.txt requirements-dev.txt
./scripts/run-tests.sh
```

## Deploy the component to development environment
The `UserManagementBackend-Dev` stage uses your default AWS account and region.
It consists of two stacks - stateful (database) and stateless (API and monitoring) 

```bash
npx cdk deploy "UserManagementBackend-Dev/*"
```

Example outputs for `npx cdk deploy "UserManagementBackend-Dev/*"`:
```text
 ✅  UserManagementBackendDevStatefulB4115ED0 (UserManagementBackend-Dev-Stateful) (no changes)

Outputs:
UserManagementBackendDevStatefulB4115ED0.ExportsOutputFnGetAttDatabaseTableF104A135ArnDAC15A6A = arn:aws:dynamodb:eu-west-1:807650736403:table/UserManagementBackend-Dev-Stateful-DatabaseTableF104A135-1JZ4KML3DEAMJ
UserManagementBackendDevStatefulB4115ED0.ExportsOutputRefDatabaseTableF104A1356B7D7D8A = UserManagementBackend-Dev-Stateful-DatabaseTableF104A135-1JZ4KML3DEAMJ
```
```text
 ✅  UserManagementBackendDevStatelessAD73535F (UserManagementBackend-Dev-Stateless)

Outputs:
UserManagementBackendDevStatelessAD73535F.APIEndpointURL = https://ctixe0v786.execute-api.eu-west-1.amazonaws.com/
```

## Deploy the pipeline
**Note:** The pipeline will deploy continuous build for pull requests

**Prerequisites**
- Create a new repository from usermanagement-backend, if you haven't done this already
- Create AWS CodeStar Connections [connection](https://docs.aws.amazon.com/dtconsole/latest/userguide/welcome-connections.html)
  for the pipeline
- Authorize AWS CodeBuild access for the continuous build
  - Start creating a new project manually
  - Select GitHub as Source provider
  - Choose **Connect using OAuth**
  - Authorize access and cancel the project creation
- Update the values in [constants.py](constants.py)
- Commit and push the changes: `git commit -a -m 'Update constants' && git push`

```bash
npx cdk deploy UserManagementBackend-Pipeline
```

## Delete all stacks
**Do not forget to delete the stacks to avoid unexpected charges**
```bash
npx cdk destroy "UserManagementBackend-Dev/*"
npx cdk destroy UserManagementBackend-Pipeline
npx cdk destroy "UserManagementBackend-Pipeline/UserManagementBackend-Prod/*"
```

Delete AWS CodeStar Connections connection if it is no longer needed. Follow the instructions
in [Delete a connection](https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-delete.html).

## Testing the web API
Below are examples that show the available resources and how to use them.

```bash
endpoint_url=$(aws cloudformation describe-stacks \
  --stack-name UserManagementBackend-Dev-Stateless \
  --query 'Stacks[*].Outputs[?OutputKey==`APIEndpointURL`].OutputValue' \
  --output text)

curl \
    -H "Content-Type: application/json" \
    -X POST \
    -d '{"username":"john", "email":"john@example.com"}' \
    "${endpoint_url}/users"

curl \
    -H "Content-Type: application/json" \
    -X GET \
    "${endpoint_url}/users/john"

curl \
    -H "Content-Type: application/json" \
    -X PUT \
    -d '{"country":"US", "state":"WA"}' \
    "${endpoint_url}/users/john"

curl \
    -H "Content-Type: application/json" \
    -X DELETE \
    "${endpoint_url}/users/john"
```
