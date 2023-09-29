#!/usr/bin/env python
import pika
import json

rabbit_host = '10.128.0.2'
rabbit_user = 'broker_user'
rabbit_password = 'isis2503'
exchange = 'loginauthentication_users'
topic = 'AUTENTICACION'

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, credentials=pika.PlainCredentials(rabbit_user, rabbit_password)))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='topic')

    usuario = input("Ingresa el nombre de usuario: ")
    clave = input("Ingresa la clave: ")

    usuario_dicc = {
        'usuario': usuario,
        'clave': clave,
    }

    payload = json.dumps(usuario_dicc)

    channel.basic_publish(exchange=exchange, routing_key=topic, body=payload)

    print('> Enviando peticion de autenticacion')

except KeyboardInterrupt:
    print("Saliendo del programa.")

finally:

    if connection.is_open:
        connection.close()
