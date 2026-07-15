# Copycat Server

## AWS Stack
- AWS API Gateway
- AWS Lambda
- AWS DynamoDB
- AWS S3

## Authentication

Basic authentication is used for API requests. The client sends base64 encrypted `<user-id>:<api-key>` in the `Authorization` header.
Lambda authorizer verifies if the user exists in DynamoDB user table and the provided API key is valid. 
The API key is stored in DynamoDB as a SHA256 hash(a 16-bytes hexadecimal salt + api_key).

## API Endpoints

### `POST /clipboard` 
sent content from local OS clipboard to the copycat server.
Support posting plain text, html and optionally an image or a file up to 5MB. `image` and `file` are mutually exclusive.
- without attachment: use content-type `application/json` with content in json format.
- with image: use `multipart/form-data` with an `image` field for the binary and a `body` field for a json body.
- with file: use `multipart/form-data` with a `file` field for the binary and a `body` field for a json body.
- request json body example:
```json
{
  "text": "Quarterly Report",
  "html": "<html>Quarterly Report</html>"
}
```

### `GET /clipboard`

Get content from copycat server to local OS clipboard. 
- response 200 `application/json` example (with image):
```json
{
  "text": "caption",
  "image": {
    "name": "photo.png",
    "url": "https://s3.amazonaws.com/bucket/key?X-Amz-Signature=..."
  }
}
```
- response 200 `application/json` example (with file):
```json
{
  "text": "Quarterly Report",
  "html": "<html>Quarterly Report</html>",
  "file": {
    "name": "report.pdf",
    "url": "https://s3.amazonaws.com/bucket/key?X-Amz-Signature=..."
  }
}
```

The `image` or `file` field is only present when the clipboard item has an attachment. The `url` is a presigned S3 URL that expires shortly after being issued — the client should download the file promptly after receiving it.

## DynamoDB Table

### User

| Column    | Type   | Description                                   |
|-----------|--------|-----------------------------------------------|
| `user-id` | String | Partition key. Unique user identifier.        |
| `api-key` | String | Hash of the API key.                          |
| `salt`    | String | 16-byte salt encoded as a hexadecimal string. |

### Clipboard

| Column     | Type   | Description                                                               |
|------------|--------|---------------------------------------------------------------------------|
| `user-id`  | String | Partition key. References the user who owns the entry.                    |
| `text`     | String | Plain text clipboard content.                                             |
| `html`     | String | HTML clipboard content.                                                   |
| `filename` | String | Original filename of the attached image or file.                          |
| `image`    | String | S3 key pointing to the clipboard image attachment.                        |
| `file`     | String | S3 key pointing to the clipboard file attachment.                         |
| `ttl`      | Number | Unix timestamp (seconds). DynamoDB auto-deletes the item after this time. |


## scripts

### `bin/add-user`

- assumes AWS CLI is configured with proper credentials and region.
- take parameters:
  - `--user-id | -u`: unique user identifier
  - `--api-key | -k`: custom API key
  - `--dry-run | -d`: dry run, do not actually add user to DynamoDB
- Generate a random 16-byte salt and hash the API key with the salt using SHA256.
- Find user table name from `.env`, create item in DynamoDB with user-id, salt and hashed API key, override value if user-id already exists.
- In non dry-run mode, print the generated salt and hashed API key in json format. In dry run mode, only print the result without actually adding the user to DynamoDB.

