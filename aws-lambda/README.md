# aws-lambda

AWS Lambda (Python) behind a Function URL. It generates a short motivational
line with Amazon Bedrock (Nova Micro) to boost productivity.

Every call rolls a random **voice** (40 personas: `friendly`, `drill_sergeant`,
`teacher`, `financial_advisor`, `pirate_captain`, `zen_monk`, …), a random
**angle** (what the line leans on) and a random **device** (how it's shaped) —
2,560 combinations, so the same task keeps producing a different push. The
message stays motivational and on the user's side in every voice.

## Request

- **POST** `/` with JSON body `{ "task": "finish the quarterly report" }`
  → returns a motivation tailored to that task.
- **GET** `/` (no task) → returns a generic motivation on a random topic.
- Optional `"voice": "drill_sergeant"` pins the persona; unknown slugs fall
  back to a random one.
- Also accepts `?task=...` and `?voice=...` as query-string parameters.

## Response

```json
{ "message": "…", "task": "…", "voice": "pirate_captain", "model": "amazon.nova-micro-v1:0" }
```

On any error it still returns HTTP 200 with a local fallback message.

## Config (env vars)

| Variable           | Default                   |
| ------------------ | ------------------------- |
| `BEDROCK_REGION`   | `us-east-1`               |
| `BEDROCK_MODEL_ID` | `amazon.nova-micro-v1:0`  |

The Lambda authenticates to Bedrock through its **IAM role** — no API key in code.
The frontend reads the Function URL from `VITE_LAMBDA_URL` in `.env`.
