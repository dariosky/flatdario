import logging

from flat import Aggregator

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    agg = Aggregator()
    # agg.send_push_notifications(
    #     {"title": "Dario Varotto published a new content",
    #      "body": "xkcd: GDPR"},
    # )
    agg.send_push_history()
