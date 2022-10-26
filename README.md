# User management backend
The project implements a *user management backend* component that uses 
Amazon API Gateway, AWS Lambda and Amazon DynamoDB to provide basic 
CRUD operations for managing users. The project also includes a toolchain 
with continuous deployment pipeline and pull request validation build.

![diagram](https://user-images.githubusercontent.com/4362270/197012024-d3b9e347-e1ba-4d60-81b1-5ff66561d94b.png)
\* Diagram generated using https://github.com/pistazie/cdk-dia

## Create a new repository from usermanagement-backend
This is optional for deploying the component to sandbox environment, but 
**required** for deploying the toolchain.

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
# Pinning pip-tools to 6.4.0 and pip to 21.3.1 due to
# https://github.com/jazzband/pip-tools/issues/1576
pip install pip-tools==6.4.0
pip install pip==21.3.1

./scripts/install-deps.sh
./scripts/run-tests.sh
```

### [Optional] Upgrade AWS CDK Toolkit version
**Note:** If you are planning to upgrade dependencies, first push the upgraded AWS CDK Toolkit version.
See [(pipelines): Fail synth if pinned CDK CLI version is older than CDK library version](https://github.com/aws/aws-cdk/issues/15519) 
for more details.

```bash
vi package.json  # Update the "aws-cdk" package version
./scripts/install-deps.sh
./scripts/run-tests.sh
```

### [Optional] Upgrade dependencies (ordered by constraints)
Consider [AWS CDK Toolkit (CLI)](https://docs.aws.amazon.com/cdk/latest/guide/reference.html#versioning) compatibility 
when upgrading AWS CDK packages version.

```bash
pip-compile --upgrade backend/api/runtime/requirements.in
pip-compile --upgrade requirements.in
pip-compile --upgrade requirements-dev.in
./scripts/install-deps.sh
# [Optional] Cleanup unused packages
pip-sync backend/api/runtime/requirements.txt requirements.txt requirements-dev.txt
./scripts/run-tests.sh
```

## Deploy the AWS Service Catalog AppRegistry application stack
[AWS Service Catalog AppRegistry](https://docs.aws.amazon.com/servicecatalog/latest/arguide/intro-app-registry.html)
allows to store your AWS applications, their associated resource collections, and 
application attribute groups. Application attribute groups define the context of 
your applications and resources.

The [app.py](app.py) module defines the AppRegistry application. The 
[operations.py](operations.py) module uses [Aspects](https://docs.aws.amazon.com/cdk/v2/guide/aspects.html)
for adding operations capabilities to each stack. The `Metadata` class in `operations.py` 
module defines an AppRegistry [attribute group](https://docs.aws.amazon.com/servicecatalog/latest/arguide/overview-appreg.html#attr-groups). 
The `Metadata` class needs the AppRegistry application ARN to associate the attribute 
group with the application. Hence, you should deploy the AppRegistry application first, 
then store the application ARN value in the source code per instructions below.

- Update the AppRegistry application environment in [app.py](app.py)
- Commit and push the changes: `git commit -a -m 'Update AppRegistry application environment' && git push`

```bash
npx cdk deploy ApplicationAssociatorStack
aws cloudformation describe-stacks \
  --stack-name UserManagementBackendApplication \
  --query 'Stacks[*].Outputs[?OutputKey==`AppRegistryApplicationArn`].OutputValue' \
  --output text
```
- Update the `APPREGISTRY_APPLICATION_ARN` constant in [operations.py](operations.py)
- Commit and push the changes: `git commit -a -m 'Update AppRegistry application ARN' && git push`

## Deploy the backend sandbox stack
The `UserManagementBackendSandbox` stack uses your default AWS account and region. 

```bash
npx cdk deploy UserManagementBackendSandbox
```

Example output for `npx cdk deploy UserManagementBackendSandbox`:
```text
 ✅  UserManagementBackendSandbox

Outputs:
UserManagementBackendSandbox.APIEndpoint = https://bsc9goldsa.execute-api.eu-west-1.amazonaws.com/
```

## Deploy the toolchain

**Prerequisites**
- Create a new repository from usermanagement-backend, if you haven't done this already
- Create AWS CodeStar Connections [connection](https://docs.aws.amazon.com/dtconsole/latest/userguide/welcome-connections.html)
  for continuous deployment
- Authorize AWS CodeBuild access for the pull request validation
  - Start creating a new project manually
  - Select GitHub as Source provider
  - Choose **Connect using OAuth**
  - Authorize access and cancel the project creation
- Update the toolchain environment in [app.py](app.py) 
- Update the toolchain configuration in [toolchain.py](toolchain.py)
- Commit and push the changes: `git commit -a -m 'Update toolchain environment and configuration' && git push`

```bash
npx cdk deploy UserManagementBackendToolchain
```

## Delete all stacks
**Do not forget to delete the stacks to avoid unexpected charges**
```bash
npx cdk destroy UserManagementBackendSandbox
npx cdk destroy UserManagementBackendToolchain
npx cdk destroy UserManagementBackendToolchain/ContinuousDeployment/Pipeline/Production/UserManagementBackendProduction
npx cdk destroy ApplicationAssociatorStack
```

Delete the AWS CodeStar Connections connection if it is no longer needed. Follow the instructions
in [Delete a connection](https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-delete.html).

## Testing the API
Below are examples that show the available resources and how to use them.

```bash
api_endpoint=$(aws cloudformation describe-stacks \
  --stack-name UserManagementBackendSandbox \
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
    -d '{"country":"US", "state":"WA"}' \
    "${api_endpoint}/users/john"

curl \
    -H "Content-Type: application/json" \
    -X DELETE \
    "${api_endpoint}/users/john"
```
