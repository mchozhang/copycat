import base64
import email
import json
import os
import time

import boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

CLIPBOARD_BUCKET = os.environ["CLIPBOARD_BUCKET"]
CLIPBOARD_TABLE = os.environ["DDB_CLIPBOARD_TABLE"]
USER_TABLE = os.environ["DDB_USER_TABLE"]
CLIPBOARD_TTL = int(os.environ["CLIPBOARD_TTL"])


def get_s3_presigned_url(key: str, expires_in: int = CLIPBOARD_TTL) -> str:
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": CLIPBOARD_BUCKET, "Key": key},
        ExpiresIn=expires_in,
    )


def get_clipboard(event):
    user_id = get_user_id(event)
    table = dynamodb.Table(CLIPBOARD_TABLE)
    item = table.get_item(Key={"user-id": user_id}).get("Item")

    if not item:
        return resp(404, {"message": "No clipboard content found"})

    body = dict()
    if "text" in item:
        body["text"] = item["text"]
    if "html" in item:
        body["html"] = item["html"]
    if "file" in item:
        body["file"] = {
            "name": item.get("filename", "file"),
            "url": get_s3_presigned_url(item.get("filename", "file")),
        }
    if "image" in item:
        body["image"] = {
            "name": item.get("filename", "image.png"),
            "url": get_s3_presigned_url(item["image"]),
        }

    return resp(200, body)


def post_clipboard(event):
    user_id = get_user_id(event)
    content_type = event.get("headers", {}).get("content-type", "")
    table = dynamodb.Table(CLIPBOARD_TABLE)
    ttl = int(time.time()) + CLIPBOARD_TTL
    ddb_item = {
        "user-id": user_id,
        "ttl": ttl
    }

    if "multipart/form-data" in content_type:
        # with image or file attachment
        file_data, file_name, field_name, body = parse_multipart(event, content_type)
        if not file_data or not file_name:
            return resp(400, {"message": "Missing file or filename in Content-Disposition"})
        s3.put_object(Bucket=CLIPBOARD_BUCKET, Key=user_id, Body=file_data)
        ddb_item[field_name] = f"{user_id}/{field_name}"  # "image" or "file" as the DDB key
        ddb_item["filename"] = file_name
    else:
        # without file — remove any existing S3 object for this user
        body = json.loads(event.get("body") or "{}")
        s3.delete_object(Bucket=CLIPBOARD_BUCKET, Key=user_id)

    if text := body.get("text"):
        ddb_item["text"] = text
    if html := body.get("html"):
        ddb_item["html"] = html

    table.put_item(Item=ddb_item)
    return resp(201, {})


def parse_multipart(event, content_type):
    """
    parse multipart form data from http body, sample unencrypted body:
    ------FormBoundary7MA4YWxkTrZu0gW
    Content-Disposition: form-data; name="file"; filename="example.txt"
    Content-Type: text/plain

    Hello, this is the clipboard file content.
    ------FormBoundary7MA4YWxkTrZu0gW
    Content-Disposition: form-data; name="image"; filename="image.png"
    Content-Type: image/png

    <image-binary-data>
    ------FormBoundary7MA4YWxkTrZu0gW
    Content-Disposition: form-data; name="body"
    Content-Type: application/json

    {"text": "Hello", "html": "<p>Hello</p>"}
    ------FormBoundary7MA4YWxkTrZu0gW--
    :param event: lambda event
    :param content_type: http content-type header
    :return: (file_data, file_name, field_name, body_json)
    """
    raw_body = event.get("body", "")
    body_bytes = base64.b64decode(raw_body) if event.get("isBase64Encoded") else raw_body.encode()

    # Prepend content-type header so the email parser can read the boundary
    msg = email.message_from_bytes(f"Content-Type: {content_type}\r\n\r\n".encode() + body_bytes)

    file_data = None
    file_name = None
    field_name = None
    body_json = dict()

    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        name = part.get_param("name", header="content-disposition")
        if name in ("image", "file"):
            file_data = part.get_payload(decode=True)
            file_name = part.get_filename()
            field_name = name
        elif name == "body":
            body_json = json.loads(part.get_payload(decode=True))

    return file_data, file_name, field_name, body_json


def get_user_id(event):
    return event["requestContext"]["authorizer"]["userId"]


def resp(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    method = event["httpMethod"]
    path = "/" + event["pathParameters"]["proxy"]

    if path == "/clipboard":
        if method == "GET":
            return get_clipboard(event)
        if method == "POST":
            return post_clipboard(event)
        return resp(405, {"message": "Method not allowed"})

    return resp(404, {"message": "Not found"})


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            event = json.load(f)
    else:
        event = json.load(sys.stdin)

    result = lambda_handler(event, None)
    print(json.dumps(result, indent=2))
