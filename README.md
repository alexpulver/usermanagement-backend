# User management service
The project implements a *user management* service that uses Amazon API Gateway, 
AWS Lambda and Amazon DynamoDB to provide a CRUD API for managing users. The project 
also includes a toolchain with continuous deployment pipeline and pull request 
validation build.

![diagram](https://github.com/alexpulver/usermanagement/assets/4362270/c80dab6d-2921-4d69-9838-b9be0eccd40f)
\* Diagram generated using https://github.com/pistazie/cdk-dia

## Create development environment
See [Getting Started With the AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
for additional details and prerequisites

## Clone the code
```bash
git clone https://github.com/alexpulver/usermanagement
cd usermanagement
```

## Fork the repository
This is **optional** for deploying the service to sandbox environment, but 
**required** for deploying the toolchain.

```bash
git remote set-url origin <your fork URL>
```

## Configure local environment
```bash
python3.9 -m venv .venv
source .venv/bin/activate

# [Optional] Needed to upgrade dependencies and cleanup unused packages
# Pinning pip-tools to 6.4.0 and pip to 21.3.1 due to
# https://github.com/jazzband/pip-tools/issues/1576
pip install pip-tools==6.13.0
pip install pip==23.1.2

./scripts/install-deps.sh
./scripts/run-tests.sh
```

## [Optional] Upgrade AWS CDK Toolkit version
**Note:** If you are planning to upgrade dependencies, first push the upgraded AWS CDK Toolkit version.
See [(pipelines): Fail synth if pinned CDK CLI version is older than CDK library version](https://github.com/aws/aws-cdk/issues/15519) 
for more details.

```bash
vi package.json  # Update the "aws-cdk" package version
./scripts/install-deps.sh
./scripts/run-tests.sh
```

## [Optional] Upgrade dependencies (ordered by constraints)
Consider [AWS CDK Toolkit (CLI)](https://docs.aws.amazon.com/cdk/latest/guide/reference.html#versioning) compatibility 
when upgrading AWS CDK packages version.

```bash
pip-compile --upgrade infrastructure/requirements.in
pip-compile --upgrade runtime/api/requirements.in
pip-compile --upgrade requirements-dev.in
./scripts/install-deps.sh
# [Optional] Cleanup unused packages
pip-sync \
  infrastructure/requirements.txt \
  runtime/api/requirements.txt \
  requirements-dev.txt
./scripts/run-tests.sh
```

## Deploy metadata management environment stack
The service uses [AWS Service Catalog AppRegistry](https://docs.aws.amazon.com/servicecatalog/latest/arguide/intro-app-registry.html) 
to manage application metadata.

**Prerequisites**
- Update the `MANAGEMENT_ENVIRONMENT` constant in [infrastructure/constants.py](infrastructure/constants.py)
- Commit and push the changes: `git commit -a -m 'Management environment' && git push`

```bash
npx cdk deploy UserManagement-Metadata-Management
```

## Deploy components sandbox environment stack
The `UserManagement-Components-Sandbox` stack uses your default AWS account and region. 

```bash
npx cdk deploy UserManagement-Components-Sandbox
```

Example output for `npx cdk deploy UserManagement-Components-Sandbox`:
```text
 ✅  UserManagement-Components-Sandbox

Outputs:
UserManagement-Components-Sandbox.APIEndpoint = https://bsc9goldsa.execute-api.eu-west-1.amazonaws.com/
```

## Deploy toolchain management environment stack

**Prerequisites**
- Fork the repository, if you haven't done this already
- Create AWS CodeStar Connections [connection](https://docs.aws.amazon.com/dtconsole/latest/userguide/welcome-connections.html)
  for the continuous deployment pipeline
- Authorize AWS CodeBuild access for the pull request validation build
  - Start creating a new project manually
  - Select GitHub as Source provider
  - Choose **Connect using OAuth**
  - Authorize access and cancel the project creation
- Update the `GITHUB_CONNECTION_ARN`, `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_TRUNK_BRANCH`,
  `COMPONENTS_ENVIRONMENTS` constants in [infrastructure/constants.py](infrastructure/constants.py)
- Commit and push the changes: `git commit -a -m 'Source configuration and components environments' && git push`

```bash
npx cdk deploy UserManagement-Toolchain-Management
```

## Delete all stacks
**Do not forget to delete the stacks to avoid unexpected charges**
```bash
npx cdk destroy UserManagement-Toolchain-Management
npx cdk destroy UserManagement-Components-Production
npx cdk destroy UserManagement-Components-Sandbox
npx cdk destroy UserManagement-Metadata-Management
```

Delete the AWS CodeStar Connections connection if it is no longer needed. Follow the instructions
in [Delete a connection](https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-delete.html).

## Testing
Below are examples that show the available resources and how to use them.

```bash
api_endpoint=$(aws cloudformation describe-stacks \
  --stack-name UserManagement-Components-Sandbox \
  --query 'Stacks[*].Outputs[?OutputKey==`APIEndpoint`].OutputValue' \
  --output text)

curl \
    -H "Content-Type: application/json" \
    -X POST \
    -d '{"username":"john", "email":"john@example.com"}' \
    "${api_endpoint}/users"

curl \
    -H "Content-Type: application/json" \
    -X GET \
    "${api_endpoint}/users/john"

curl \
    -H "Content-Type: application/json" \
    -X PUT \
    -d '{"username":"john", "country":"US", "state":"WA"}' \
    "${api_endpoint}/users/john"

curl \
    -H "Content-Type: application/json" \
    -X DELETE \
    "${api_endpoint}/users/john"
```
