# User management backend
The application implements a *user management backend* service that uses Amazon API Gateway, AWS Lambda and Amazon DynamoDB to provide a CRUD API for managing users. The application also includes a toolchain with deployment pipeline and pull request build.

![diagram](https://github.com/alexpulver/usermanagement-backend/assets/4362270/774430b7-5315-44b0-9083-8d90d1a130a1)
\* Diagram generated using https://github.com/pistazie/cdk-dia

## Create development environment
See [Getting Started With the AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
for additional details and prerequisites

## Clone the code
```bash
git clone https://github.com/alexpulver/usermanagement-backend
cd usermanagement-backend
```

## Fork the repository
This is **optional** for deploying the service to sandbox environment, but 
**required** for deploying the toolchain.

```bash
git remote set-url origin <your fork URL>
```

## Configure local environment
```bash
python3.11 -m venv .venv
source .venv/bin/activate

# [Optional] Use pip-tools to upgrade dependencies
# Pinning pip-tools to 6.4.0 and pip to 21.3.1 due to
# https://github.com/jazzband/pip-tools/issues/1576
pip install pip-tools==6.4.0
pip install pip==21.3.1

./scripts/install-deps.sh
./scripts/run-tests.sh
```

## [Optional] Upgrade AWS CDK Toolkit version
**Note:** If you are planning to upgrade dependencies, first push the upgraded AWS CDK Toolkit version.
See [This CDK CLI is not compatible with the CDK library used by your application](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.pipelines-readme.html#this-cdk-cli-is-not-compatible-with-the-cdk-library-used-by-your-application) 
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
pip-compile --upgrade service/api/requirements.in
pip-compile --upgrade requirements.in
pip-compile --upgrade requirements-dev.in

./scripts/install-deps.sh
./scripts/run-tests.sh
```

## Deploy application stack
The application uses [AWS Service Catalog AppRegistry](https://docs.aws.amazon.com/servicecatalog/latest/arguide/intro-app-registry.html) 
to manage application metadata.

**Prerequisites**
- Update the account for `APPLICATION_PRODUCTION_ENVIRONMENT` constant in [constants.py](constants.py)
- Commit and push the changes: `git commit -a -m 'Environment configuration' && git push`

```bash
npx cdk deploy UserManagementBackend-Application-Production
```

## Deploy service stack
The `UserManagementBackend-Service-Sandbox` stack uses your default AWS account and Region. 

```bash
npx cdk deploy UserManagementBackend-Service-Sandbox
```

Example output for `npx cdk deploy UserManagementBackend-Service-Sandbox`:
```text
 ✅  UserManagementBackend-Service-Sandbox

Outputs:
UserManagementBackend-Service-Sandbox.APIEndpoint = https://bsc9goldsa.execute-api.eu-west-1.amazonaws.com/
```

## Deploy toolchain stack

**Prerequisites**
- Fork the repository, if you haven't done this already
- Create AWS CodeStar Connections [connection](https://docs.aws.amazon.com/dtconsole/latest/userguide/welcome-connections.html)
  for the deployment pipeline
- Authorize AWS CodeBuild access for the pull request build
  - Start creating a new project manually
  - Select GitHub as Source provider
  - Choose **Connect using OAuth**
  - Authorize access and cancel the project creation
- Update the `GITHUB_CONNECTION_ARN`, `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_TRUNK_BRANCH`,
  `TOOLCHAIN_PRODUCTION_ENVIRONMENT`, `SERVICE_SHARED_ENVIRONMENTS` constants in [constants.py](constants.py)
- Commit and push the changes: `git commit -a -m 'Source and environments configuration' && git push`

```bash
npx cdk deploy UserManagementBackend-Toolchain-Production
```

## Delete all stacks
**Do not forget to delete the stacks to avoid unexpected charges**
```bash
npx cdk destroy UserManagementBackend-Toolchain-Production
npx cdk destroy UserManagementBackend-Service-Production
npx cdk destroy UserManagementBackend-Service-Sandbox
npx cdk destroy UserManagementBackend-Application-Production
```

Delete the AWS CodeStar Connections connection if it is no longer needed. Follow the instructions
in [Delete a connection](https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-delete.html).

## Testing
Below are examples that show the available resources and how to use them.

```bash
api_endpoint=$(aws cloudformation describe-stacks \
  --stack-name UserManagementBackend-Service-Sandbox \
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
    "${api_endpoint}/users"

curl \
    -H "Content-Type: application/json" \
    -X DELETE \
    "${api_endpoint}/users/john"
```
