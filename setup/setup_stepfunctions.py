import boto3
import json
import os

endpoint = "http://localhost:4566"
region = "eu-west-1"


def create_state_machine(name, definition_path):
    sfn = boto3.client("stepfunctions", endpoint_url=endpoint, region_name=region)

    try:
        response = sfn.list_state_machines()
        state_machines = response.get("stateMachines", [])

        for sm in state_machines:
            if sm["name"] == name:
                print(f"State machine {name} already exists. Deleting it...")
                sfn.delete_state_machine(stateMachineArn=sm["stateMachineArn"])
                break

    except Exception as e:
        print(f"Error checking or deleting state machine: {str(e)}")

    with open(definition_path) as f:
        definition = json.load(f)

    response = sfn.create_state_machine(
        name=name,
        definition=json.dumps(definition),
        roleArn="arn:aws:iam::000000000000:role/StepFunctionRole"  # Rolę IAM dla LocalStack
    )

    print(f"Created Step Function: {name}")
    print(f"State Machine ARN: {response['stateMachineArn']}")


if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), "../retry_flow/step_function_def.json")
    create_state_machine("order-processing-flow", file_path)
