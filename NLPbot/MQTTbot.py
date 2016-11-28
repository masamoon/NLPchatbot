import pika
import time
from chatbot import chatbot



chatbot = chatbot()
credentials = pika.PlainCredentials('es', 'imhere')
parameters = pika.ConnectionParameters('192.168.8.217',
                                       5012,
                                       '/',
                                       credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    time.sleep(body.count(b'.'))
    response_bot = chatbot.run_bot(body)
    print(" [x] Response: "+response_bot)
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='task_queue')


channel.start_consuming()





