import json
import time
from pika import BlockingConnection, ConnectionParameters
from pymongo import MongoClient
'''
İnterpolScraper'dan alınan veriler burda mongo veritabanına aktarılır 
'''
class QueueConsumer:
    def __init__(self, queue_host, queue_name, mongo_host):
        self.queue_host = queue_host
        self.queue_name = queue_name
        self.mongo_host = mongo_host

    def consume_queue(self):
        connection_params = ConnectionParameters(host=self.queue_host)
        with BlockingConnection(connection_params) as connection:
            channel = connection.channel()
            channel.queue_declare(queue=self.queue_name)

            def callback(ch, method, properties, body):
                data = json.loads(body)
                self.save_to_mongo(data)
                print(f"Received and processed: {data}")

            channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
            print('Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()

    def save_to_mongo(self, data):
        client = MongoClient(self.mongo_host)
        db = client['interpol_database']
        collection = db['interpol_data']
        collection.insert_one(data)

if __name__ == "__main__":
    
    time.sleep(30)
    queue_consumer = QueueConsumer("rabbitmq", "interpol_queue", "mongo")
    queue_consumer.consume_queue()
