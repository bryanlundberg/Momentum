import base64
import json
import os
import random

import boto3
from botocore.config import Config

_REGION = os.environ.get("BEDROCK_REGION", "us-east-1")
_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0")

_bedrock = boto3.client(
    "bedrock-runtime",
    region_name=_REGION,
    config=Config(retries={"max_attempts": 2, "mode": "standard"}),
)

_CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
}

_TOPICS = [
    "taking the first step",
    "focus and concentration",
    "beating procrastination",
    "consistency and habits",
    "priorities and saying no",
    "energy and smart rest",
    "progress over perfection",
]

_FALLBACK_MESSAGES = [
    "Start small, but start today.",
    "Progress lives in action, not intention.",
    "One finished task beats ten planned ones.",
    "Do it imperfectly, but do it now.",
]

_MAX_TASK_LEN = 300


def _response(status, body):
    return {
        "statusCode": status,
        "headers": _CORS,
        "body": json.dumps(body, ensure_ascii=False),
    }


def _extract_task(event):
    body = event.get("body")
    if body:
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode("utf-8", "ignore")
        try:
            data = json.loads(body)
            if isinstance(data, dict) and data.get("task"):
                return str(data["task"]).strip()[:_MAX_TASK_LEN]
        except (ValueError, TypeError):
            pass

    params = event.get("queryStringParameters") or {}
    if params.get("task"):
        return str(params["task"]).strip()[:_MAX_TASK_LEN]

    return ""


def _build_prompt(task):
    if task:
        return (
            'A person needs to accomplish this task: "' + task + '". '
            "Write ONE short, original motivational sentence in English "
            "(max 20 words) that speaks directly to them about getting this "
            "specific task done and boosting their productivity. "
            "No quotes, no author, no emojis. Reply with the sentence only."
        )

    topic = random.choice(_TOPICS)
    return (
        "Generate ONE short, original motivational sentence in English "
        "(max 16 words) about " + topic + ". "
        "It must inspire productivity. No quotes, no author, no emojis. "
        "Reply with the sentence only."
    )


def _generate_message(task):
    prompt = _build_prompt(task)

    response = _bedrock.converse(
        modelId=_MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 60, "temperature": 0.9, "topP": 0.9},
    )

    text = response["output"]["message"]["content"][0]["text"].strip()
    text = text.strip('"').strip("'").strip()
    return text or random.choice(_FALLBACK_MESSAGES)


def lambda_handler(event, context):
    method = (
        event.get("requestContext", {})
        .get("http", {})
        .get("method", event.get("httpMethod", "GET"))
    )
    if method == "OPTIONS":
        return _response(200, {"ok": True})

    try:
        task = _extract_task(event)
        message = _generate_message(task)
        return _response(200, {"message": message, "task": task, "model": _MODEL_ID})
    except Exception as exc:
        print("Error generating message:", repr(exc))
        return _response(
            200,
            {
                "message": random.choice(_FALLBACK_MESSAGES),
                "fallback": True,
                "error": str(exc),
            },
        )
