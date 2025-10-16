import json
import time
from pathlib import Path
from google.auth import default
from google import pubsub
from . import app


@app.command(
    name="pubsub_pull",
)
def pubsub_pull(
        subscription: str,
        n=1,
        output_path='.',
):
    """
    Pull messages from a Google Cloud Pub/Sub subscription and save them as JSON files.

    """
    credentials, project_id = default()
    print(f'Pull up to {n} messages from topic {subscription} to {output_path}')
    subscriber = pubsub.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription)
    response = subscriber.pull(
        request={
            "subscription": subscription_path,
            "max_messages": int(n)
        }
    )

    if len(response.received_messages) == 0:
        print("No new messages in the queue. Waiting...")
        return

    pwd = Path(output_path)
    pwd.mkdir(parents=True, exist_ok=True)

    def callback(message: pubsub.PubsubMessage):
        filename = f"{message.message_id}.json"
        (pwd / filename).write_text(json.dumps(json.loads(message.data.decode('utf-8')), indent=2))
        print(f"Save message {message.message_id} to {filename}")

    for message in response.received_messages:
        callback(message.message)