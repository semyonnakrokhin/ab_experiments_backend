from kombu import Exchange, Queue

from apps.src.task_queue.config import celery_settings

broker_url = celery_settings.broker.broker_url
result_backend = celery_settings.result_backend.result_backend_url

task_track_started = True
task_serializer = "json"
result_serializer = "json"
accept_content = ["pickle", "json"]
result_expires = 200
result_persistent = False
worker_send_task_events = False
worker_prefetch_multiplier = 4

# Set queues config
default_queue_name = "default"
default_exchange_name = "default_exchange"
default_routing_key = "experiments.default"

default_exchange = Exchange(default_exchange_name, type="direct")

default_queue = Queue("default", exchange=default_exchange, routing_key="default")

button_color_queue = Queue(
    "button", exchange=default_exchange, routing_key="experiments.button.color"
)

price_queue = Queue("price", exchange=default_exchange, routing_key="experiments.price")
task_queues = (default_queue, button_color_queue, price_queue)

# Set task routing config
task_default_queue = default_queue_name
task_default_exchange = default_exchange_name
task_default_routing_key = default_routing_key


# Set tasks for celery workers
include = [
    "apps.src.task_queue.tasks",
]


if __name__ == "__main__":
    print(broker_url)
    print(result_backend)
