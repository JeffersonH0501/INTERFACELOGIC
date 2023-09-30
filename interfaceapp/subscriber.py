import pika

rabbit_host = '10.128.0.2'
rabbit_user = 'broker_user'
rabbit_password = 'isis2503'
exchange = 'loginauthentication_users'
topics = ['LOGIN']

respuesta_autenticacion = ""  # Variable global para almacenar la respuesta
detener_consumo = False  # Bandera para detener la consumición

def callback(ch, method, properties, body):
    global respuesta_autenticacion  # Indica que estamos utilizando la variable global
    global detener_consumo  # Indica que estamos utilizando la bandera global
    respuesta_autenticacion = body.decode('utf-8')
    print(respuesta_autenticacion)
    detener_consumo = True
        
def recibir_respuesta_autenticacion():
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, credentials=pika.PlainCredentials(rabbit_user, rabbit_password)))
    channel = connection.channel()

    # Declarar el intercambio (exchange) de mensajes
    channel.exchange_declare(exchange=exchange, exchange_type='topic')
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue

    for topic in topics:
        channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=topic)

    # Configurar el consumo de la cola de respuestas
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print('> Esperando respuesta para la solicitud.')

    # Comenzar a consumir mensajes
    while not detener_consumo:
        connection.process_data_events()


