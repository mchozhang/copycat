import base64
import hashlib
import os

import boto3

dynamodb = boto3.resource("dynamodb")
USER_TABLE = os.environ["DDB_USER_TABLE"]


def lambda_handler(event, context):
    token = event.get("authorizationToken", "")
    method_arn = event.get("methodArn", "")

    try:
        if token.lower().startswith("basic "):
            token = token[6:]
        decoded = base64.b64decode(token).decode("utf-8")
        user_id, api_key = decoded.split(":", 1)
    except Exception:
        raise Exception("Unauthorized")

    table = dynamodb.Table(USER_TABLE)
    item = table.get_item(Key={"user-id": user_id}).get("Item")

    if not item:
        raise Exception("Unauthorized")

    salt = item["salt"]
    stored_hash = item["api-key"]
    computed_hash = hashlib.sha256((salt + api_key).encode()).hexdigest()

    if computed_hash != stored_hash:
        raise Exception("Unauthorized")

    return _build_policy(user_id, "Allow", method_arn)


def _build_policy(user_id, effect, method_arn):
    # Wildcard to allow all methods/paths on this API stage
    parts = method_arn.split(":")
    region = parts[3]
    account_id = parts[4]
    api_id, stage = parts[5].split("/")[:2]
    resource_arn = f"arn:aws:execute-api:{region}:{account_id}:{api_id}/{stage}/*/*"

    return {
        "principalId": user_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource_arn,
                }
            ],
        },
        "context": {
            "userId": user_id,
        },
    }
