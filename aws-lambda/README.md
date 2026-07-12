# aws-lambda

AWS Lambda (Python) behind a Function URL. It generates a short motivational
line with Amazon Bedrock (Nova Micro) to boost productivity.

## Request

- **POST** `/` with JSON body `{ "task": "finish the quarterly report" }`
  → returns a motivation tailored to that task.
- **GET** `/` (no task) → returns a generic motivation on a random topic.
- Also accepts `?task=...` as a query-string parameter.

## Response

```json
{ "message": "…", "task": "…", "model": "amazon.nova-micro-v1:0" }
```

On any error it still returns HTTP 200 with a local fallback message.

## Config (env vars)

| Variable           | Default                   |
| ------------------ | ------------------------- |
| `BEDROCK_REGION`   | `us-east-1`               |
| `BEDROCK_MODEL_ID` | `amazon.nova-micro-v1:0`  |

The Lambda authenticates to Bedrock through its **IAM role** — no API key in code.
The frontend reads the Function URL from `VITE_LAMBDA_URL` in `.env`.
