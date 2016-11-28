import pika
import time
import sys
from chatbot import chatbot
import json


chatbot = chatbot()
credentials = pika.PlainCredentials('es', 'imhere')
parameters = pika.ConnectionParameters('192.168.215.165',
                                       5012,
                                       '/',
                                       credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='hello', durable=False)

message = json.dumps({'op_id':0,'user_id':'chatbot','hash':'bot19','user_name':'bot19','device_token':''})
#message = "Sou o bot"
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
print(" [x] Sent %r" % message)
#connection.close()

channel = connection.channel()

channel.queue_declare(queue='bot19', durable=False)
print(' [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    time.sleep(body.count(b'.'))
   # response_bot = chatbot.run_bot(body)
   # print(" [x] Response: "+str(response_bot))
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='bot19')


channel.start_consuming()








