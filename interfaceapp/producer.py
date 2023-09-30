#!/usr/bin/env python
import pika
import json

rabbit_host = '10.128.0.2'
rabbit_user = 'broker_user'
rabbit_password = 'isis2503'
exchange = 'loginauthentication_users'
topic = 'AUTENTICACION'

def enviar_peticion_autenticacion(usuario, clave):
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, credentials=pika.PlainCredentials(rabbit_user, rabbit_password)))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='topic')

    channel.basic_publish(exchange=exchange, routing_key=topic, body=f"{usuario} {clave}")

    print('> Solicitud de autenticacion enviada')
