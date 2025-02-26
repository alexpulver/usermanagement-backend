# User management backend
A CRUD API to manage users. Main components are the toolchain and the service. The application implements [Application Design Framework (ADF)](https://applicationdesignframework.com/) guidelines for organizing resources configuration and business logic code.

![](architecture.png)
\* Diagram generated using https://github.com/pistazie/cdk-dia

## Clone code
```bash
git clone https://github.com/alexpulver/usermanagement-backend
cd usermanagement-backend
```

## Fork repository
This is **optional** for deploying the service to sandbox environment, but **required** for deploying the toolchain.

```bash
git remote set-url origin <your fork URL>
```

## Configure development environment
```bash
python3.11 -m venv .venv
source .venv/bin/activate

# [Optional] Use pip-tools to upgrade dependencies
# Pinning pip-tools to 6.4.0 and pip to 21.3.1 due to
# https://github.com/jazzband/pip-tools/issues/1576
pip install pip-tools==6.4.0
pip install pip==21.3.1

toolchain/scripts/install-deps.sh
toolchain/scripts/run-tests.sh
```

## [Optional] Upgrade AWS CDK CLI version
If you are planning to upgrade dependencies, first push the upgraded AWS CDK CLI version. See [This CDK CLI is not compatible with the CDK library used by your application](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.pipelines-readme.html#this-cdk-cli-is-not-compatible-with-the-cdk-library-used-by-your-application) for more details.

The application uses Node Package Manager (npm) and `package.json` configuration file to install AWS CDK CLI locally. To find the latest AWS CDK CLI version: `npm view aws-cdk version`.

```bash
vi package.json  # Update the "aws-cdk-lib" package version
```

```bash
toolchain/scripts/install-deps.sh
toolchain/scripts/run-tests.sh
```

## [Optional] Upgrade dependencies (ordered by constraints)
Consider [AWS CDK CLI](https://docs.aws.amazon.com/cdk/latest/guide/reference.html#versioning) compatibility when upgrading AWS CDK packages version.

```bash
pip-compile --upgrade service/api/app/requirements.in
pip-compile --upgrade requirements.in
pip-compile --upgrade requirements-dev.in
```

```bash
toolchain/scripts/install-deps.sh
toolchain/scripts/run-tests.sh
```

## [Optional] Cleanup unused packages
```bash
pip-sync service/api/app/requirements.txt requirements.txt requirements-dev.txt
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
- Create AWS CodeConnections [connection](https://docs.aws.amazon.com/dtconsole/latest/userguide/welcome-connections.html)
  for the deployment pipeline
- Authorize AWS CodeBuild access for the pull request build
  - Start creating a new project manually
  - Select GitHub as Source provider
  - Choose **Connect using OAuth**
  - Authorize access and cancel the project creation
- Update the `GITHUB_CONNECTION_ARN`, `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_TRUNK_BRANCH`,
  `TOOLCHAIN_PRODUCTION_ENVIRONMENT`, `SERVICE_PRODUCTION_ENVIRONMENT` constants in [constants.py](constants.py)
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
```

Delete the AWS CodeConnections connection if it is no longer needed. Follow the instructions
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
