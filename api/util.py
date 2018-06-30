import logging

from graphql_relay.node.node import from_global_id

logger = logging.getLogger('flat.util')


def change_sizes(sizes, db):
    for size, ids in sizes.items():
        for gid in ids:
            id_type, rid = from_global_id(gid)
            item = db.getitem(rid)
            current_size = item.get('size')
            if current_size != size:
                logger.info(f"Changing size of {item['title']}: {current_size}=>{size}")
                item['size'] = size
                db.upsert(item, update=True)


if __name__ == '__main__':
    from flat import Aggregator

    logging.basicConfig(level=logging.INFO)
    agg = Aggregator()
    change_sizes(
        {
            "M": (
                "SXRlbVR5cGU6ZzRIYnoyakx4dlE=",
                "SXRlbVR5cGU6eE90S1dyWEh3VTA=",
                "SXRlbVR5cGU6QjhCYmROUmFOdW8=",
                "SXRlbVR5cGU6dGFnOnJzcy5kYXJpb3NreS5pdCwyMDE4LTAzLTE0Oi80OTU1",
                "SXRlbVR5cGU6MzU5MzczNDcz",
                "SXRlbVR5cGU6Sm96QW1YbzJiREU=",
                "SXRlbVR5cGU6MzQ3MjEzNTQ1OTY=",
            ),
            "L": (
                "SXRlbVR5cGU6NWE5NzQyYjU5YjI0YmQ1NTY3NjcwMmY5",
                "SXRlbVR5cGU6NTllYjBhYjcyMWNmOGEzOWY5ODNiOWJh",
                "SXRlbVR5cGU6NTliNDViNzkyMWYzM2YwOTAyNTA3NGVj",
                "SXRlbVR5cGU6elV6UlMxZmhTbjA=",
                "SXRlbVR5cGU6aXBjM09PREJGZ00=",

            )
        },
        agg.db
    )
