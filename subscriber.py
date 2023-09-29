import pika
import json
import uuid

rabbit_host = '10.128.0.2'
rabbit_user = 'broker_user'
rabbit_password = 'isis2503'
exchange = 'loginauthentication_users'
topics = ['LOGIN']

request_id = str(uuid.uuid4())

try:
    # Configurar la conexión a RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, credentials=pika.PlainCredentials(rabbit_user, rabbit_password)))
    channel = connection.channel()

    # Declarar el intercambio (exchange) de mensajes
    channel.exchange_declare(exchange=exchange, exchange_type='topic')

    # Declarar la cola para las respuestas
    response_queue = f'RESPUESTA_{request_id}'
    channel.queue_declare(queue=response_queue)

    def callback(ch, method, properties, body):
        response = json.loads(body)
        if 'request_id' in response and response['request_id'] == request_id:
            print(f'Respuesta recibida para la solicitud {request_id}: {response}')
            # Aquí puedes manejar la respuesta como desees

    # Configurar el consumo de la cola de respuestas
    channel.basic_consume(queue=response_queue, on_message_callback=callback, auto_ack=True)

    print(f'> Esperando respuesta para la solicitud {request_id}. Para salir, presiona CTRL+C')

    # Comenzar a consumir mensajes
    channel.start_consuming()

except KeyboardInterrupt:
    print("Saliendo del programa.")

finally:
    # Cerrar la conexión al finalizar
    if connection.is_open:
        connection.close()