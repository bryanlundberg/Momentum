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

# Each voice is (slug, directive). The directive is dropped verbatim into the
# prompt, so it must read as an instruction about *how* to speak.
_VOICES = [
    ("friendly", "a warm close friend who genuinely believes in them"),
    ("drill_sergeant", "a military drill sergeant barking a short, clipped order"),
    ("teacher", "a patient teacher explaining why this step matters"),
    ("financial_advisor", "a financial advisor talking about return on invested effort"),
    ("sports_coach", "a locker-room coach at halftime, down by one"),
    ("zen_monk", "a zen monk speaking plainly about presence and the next breath"),
    ("startup_founder", "a startup founder obsessed with shipping over polishing"),
    ("pirate_captain", "a pirate captain rallying the crew, nautical slang and all"),
    ("noir_detective", "a hard-boiled noir detective narrating in clipped shadows"),
    ("grandmother", "a loving grandmother who has seen worse and knows they'll manage"),
    ("stand_up_comic", "a stand-up comic roasting the excuse, never the person"),
    ("nature_documentary", "a nature documentary narrator observing the human at work"),
    ("astronaut", "an astronaut on comms, calm under a countdown"),
    ("chess_grandmaster", "a chess grandmaster thinking in tempo and position"),
    ("chef", "a head chef in a hot kitchen calling the pass"),
    ("surfer", "a laid-back surfer reading the set coming in"),
    ("librarian", "a librarian whispering something quietly devastating"),
    ("blacksmith", "a blacksmith speaking in heat, hammer, and iron"),
    ("air_traffic_control", "air traffic control, precise and cleared for takeoff"),
    ("poet", "a poet using one clean image, no ornament"),
    ("scientist", "a scientist stating it as a testable hypothesis"),
    ("mountaineer", "a mountaineer thinking one anchor at a time"),
    ("jazz_musician", "a jazz musician talking about groove and the downbeat"),
    ("gardener", "a gardener who trusts seasons and small waterings"),
    ("firefighter", "a firefighter triaging what burns first"),
    ("marathon_runner", "a marathon runner at kilometre thirty"),
    ("samurai", "a samurai speaking of discipline and the single cut"),
    ("game_show_host", "an over-caffeinated game show host announcing their turn"),
    ("sailor", "a sailor who knows the wind won't wait"),
    ("architect", "an architect thinking in foundations before facades"),
    ("stoic_philosopher", "a stoic philosopher on what is within their control"),
    ("hype_friend", "the loudest friend in the group chat, all caps energy in words"),
    ("mission_control", "mission control reading off a go/no-go poll"),
    ("carpenter", "a carpenter who measures once more, then cuts"),
    ("veteran_pilot", "a veteran pilot, unbothered, hand steady on the yoke"),
    ("mentor", "a seasoned mentor who asks one sharp question and answers it"),
    ("cartographer", "a cartographer describing the first mile of an unmapped route"),
    ("boxing_cornerman", "a boxing cornerman between rounds, towel and truth"),
    ("radio_dj", "a late-night radio DJ dedicating this one to them"),
    ("lighthouse_keeper", "a lighthouse keeper who simply keeps the lamp lit"),
]

# Framing angle: what the sentence leans on.
_ANGLES = [
    "the very first physical action they can take in the next 60 seconds",
    "how small the real starting step actually is",
    "the cost of waiting another hour",
    "who they become by finishing this",
    "the relief waiting on the other side",
    "the fact that starting badly still beats not starting",
    "momentum: the second minute is easier than the first",
    "cutting the task down to something laughably doable",
]

# Rhetorical device: how the sentence is shaped.
_DEVICES = [
    "use a vivid concrete image",
    "use a sharp contrast between two things",
    "make it a direct command",
    "make it a question they can only answer by starting",
    "use plain unadorned words, no metaphor at all",
    "build it on one metaphor from that speaker's world",
    "make it punchy and under ten words",
    "let the rhythm build to the last word",
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


def _extract_voice(event):
    """Optional caller-chosen voice slug; unknown values fall back to random."""
    requested = ""

    body = event.get("body")
    if body:
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode("utf-8", "ignore")
        try:
            data = json.loads(body)
            if isinstance(data, dict) and data.get("voice"):
                requested = str(data["voice"])
        except (ValueError, TypeError):
            pass

    if not requested:
        params = event.get("queryStringParameters") or {}
        requested = str(params.get("voice") or "")

    requested = requested.strip().lower()
    for voice in _VOICES:
        if voice[0] == requested:
            return voice

    return random.choice(_VOICES)


def _build_prompt(task, voice, angle, device):
    _, persona = voice
    shared = (
        "Speak as " + persona + ". "
        "Lean the sentence on " + angle + ", and " + device + ". "
        "Stay motivational and on their side — never mocking, never mean. "
        "No quotes, no author, no emojis, no preamble. "
        "Reply with the sentence only."
    )

    if task:
        return (
            'A person needs to accomplish this task: "' + task + '". '
            "Write ONE short, original motivational sentence in English "
            "(max 20 words) that speaks directly to them about getting this "
            "specific task done. " + shared
        )

    return (
        "Generate ONE short, original motivational sentence in English "
        "(max 16 words) about " + random.choice(_TOPICS) + ". "
        "It must inspire productivity. " + shared
    )


def _generate_message(task, voice):
    prompt = _build_prompt(task, voice, random.choice(_ANGLES), random.choice(_DEVICES))

    response = _bedrock.converse(
        modelId=_MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 80, "temperature": 1.0, "topP": 0.95},
    )

    text = response["output"]["message"]["content"][0]["text"].strip()
    text = text.strip('"').strip("'").strip()
    if not text:
        raise RuntimeError("Bedrock returned an empty message")
    return text


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
        voice = _extract_voice(event)
        message = _generate_message(task, voice)
        return _response(
            200,
            {"message": message, "task": task, "voice": voice[0], "model": _MODEL_ID},
        )
    except Exception as exc:
        print("Error generating message:", repr(exc))
        return _response(500, {"error": type(exc).__name__, "detail": str(exc)})
