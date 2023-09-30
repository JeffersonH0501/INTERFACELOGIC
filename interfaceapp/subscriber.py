import pika
import json
import uuid

rabbit_host = '10.128.0.2'
rabbit_user = 'broker_user'
rabbit_password = 'isis2503'
exchange = 'loginauthentication_users'
topics = ['LOGIN']

request_id = str(uuid.uuid4())

def callback(ch, method, body):
    response = body.decode('utf-8')
    print(response)
    if 'request_id' in response and response['request_id'] == request_id:
        print(f'Respuesta recibida para la solicitud {request_id}: {response}')
        return response
        
def recibir_respuesta_autenticacion():
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, credentials=pika.PlainCredentials(rabbit_user, rabbit_password)))
    channel = connection.channel()

    # Declarar el intercambio (exchange) de mensajes
    channel.exchange_declare(exchange=exchange, exchange_type='topic')

    # Declarar la cola para las respuestas
    response_queue = f'RESPUESTA_{request_id}'
    channel.queue_declare(queue=response_queue)

    # Configurar el consumo de la cola de respuestas
    channel.basic_consume(queue=response_queue, on_message_callback=callback, auto_ack=True)

    print(f'> Esperando respuesta para la solicitud {request_id}.')

    # Comenzar a consumir mensajes
    channel.start_consuming()
