import json
import logging
import os

from pywebpush import webpush

logger = logging.getLogger("flat.push")


class PushSender:
    claim_filename = os.path.join(os.path.dirname(__file__), 'claims.json')
    private_key_filename = os.path.join(os.path.dirname(__file__), 'private_key.pem')

    if not os.path.isfile(claim_filename):
        print("claims.json not found: Please create it.")
        example_json = json.dumps({
            "sub": "mailto:your@email.com"
        })
        print(f"It should be a json with something like this: {example_json}")
        raise Exception("Missing claims.json")

    if not os.path.isfile(private_key_filename):
        print("private_key.pem not found: Please create it.")
        print("You should create a private and public keys for your messages.")
        print("Run `vapid --gen` from the `push` folder to create them.")
        raise Exception("Missing private_key.pem")

    with open(claim_filename) as f:
        claims = json.load(f)

    @classmethod
    def send_push_notification(cls, data, subscription_info):
        claims = cls.claims.copy()  # webpush change the claims
        if not isinstance(data, str):
            data = json.dumps(data)
        webpush(
            subscription_info,
            data,
            vapid_private_key=cls.private_key_filename,
            vapid_claims=claims
        )


def send_notification(data, subscription, db):
    sub_data = json.loads(subscription)
    try:
        PushSender.send_push_notification(
            data, sub_data
        )
    except Exception as e:
        logger.error(f"Error on notification:\n{e}\n{subscription}")
    else:
        logger.info(f"Nofication sent to {subscription}")
        db.set_last_notification(subscription)


def broadcast_notification(data, db):
    subitems = db.active_subscriptions()
    count = len(subitems)
    title = data.get('title', 'data')
    logger.info(f"Broadcasting `{title}` to {count} subscriber")
    for item in subitems:
        subscription = item.subscription
        send_notification(data, subscription, db)


def send_all_missing_notifications(db):
    subscriptions = db.active_subscriptions()
    if not subscriptions:
        return
    min_date = subscriptions[0].min_date
    for subscription in subscriptions[1:]:
        min_date = min(min_date, subscription.min_date)

    items = list(filter(lambda item: item['timestamp'] > min_date, db.all()))

    logger.debug(f"Notifications for {len(items)} items")

    for subitem in subscriptions:
        start_date = subitem.last_notification or subitem.subscription_date
        for item in items:
            if item['timestamp'] > start_date:
                data = dict(
                    title='Dario Varotto shared',
                    body=item['title'],
                    image=item['thumb'],
                    url=item['url']
                )
                print(f"Notifying {data} to {subitem.id}")
                send_notification(data, subitem.subscription, db)
