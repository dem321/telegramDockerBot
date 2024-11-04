import environs
import paramiko
import telebot
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from telebot.util import extract_arguments

from models import Chat, ChatConfiguration

env = environs.Env()
env.read_env()

bot = telebot.TeleBot(env('TOKEN'), parse_mode=None)

engine = create_engine(env('DATABASE_URL'))

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Hello there')
    print(message.chat.__dict__)


# @bot.message_handler(func=lambda message: True)
# def echo(message):
#     bot.send_message(message.chat.id, message.text)
#     print(message.text.split('\n'))


@bot.message_handler(commands=['docker_ps'])
def get_available_containers(message):
    with Session(engine) as session:
        chat_config = session.query(ChatConfiguration).filter_by(chat_id=message.chat.id).first()
    try:
        client.connect(hostname=chat_config.ssh_host,
                       username=chat_config.ssh_user,
                       password=chat_config.ssh_password,
                       port=chat_config.ssh_port)
        stdin, stdout, stderr = client.exec_command('docker ps --format "{{.ID}}: {{.Names}}"')
        bot.send_message(message.chat.id, stdout.read().decode())
    finally:
        client.close()


@bot.message_handler(commands=['docker_stats'])
def check_docker_stats(message):
    args = extract_arguments(message.text)
    with Session(engine) as session:
        chat_config = session.query(ChatConfiguration).filter_by(chat_id=message.chat.id).first()
    try:
        client.connect(hostname=chat_config.ssh_host,
                       username=chat_config.ssh_user,
                       password=chat_config.ssh_password,
                       port=chat_config.ssh_port)
        stdin, stdout, err = client.exec_command(
            f'docker stats --no-stream {args} --format "{{{{.Name}}}}: {{{{.CPUPerc}}}}, {{{{.MemPerc}}}}"')
        bot.send_message(message.chat.id, stdout.read().decode() or 'no')
    finally:
        client.close()


@bot.message_handler(commands=['docker_restart'])
def restart_container(message):
    args = extract_arguments(message.text)
    with Session(engine) as session:
        chat_config = session.query(ChatConfiguration).filter_by(chat_id=message.chat.id).first()
    try:
        client.connect(hostname=chat_config.ssh_host,
                       username=chat_config.ssh_user,
                       password=chat_config.ssh_password,
                       port=chat_config.ssh_port)
        command = f'docker restart {args}'
        stdin, stdout, err = client.exec_command(command)
        bot.send_message(message.chat.id, stdout.read().decode())
    finally:
        client.close()


@bot.message_handler(commands=['docker_logs'])
def get_docker_logs(message):
    args = extract_arguments(message.text)
    with Session(engine) as session:
        chat_config = session.query(ChatConfiguration).filter_by(chat_id=message.chat.id).first()
    try:
        client.connect(hostname=chat_config.ssh_host,
                       username=chat_config.ssh_user,
                       password=chat_config.ssh_password,
                       port=chat_config.ssh_port)
        command = f'docker logs {args}'
        stdin, stdout, err = client.exec_command(command)
        bot.send_document(message.chat.id, stdout)
    finally:
        client.close()


@bot.message_handler(content_types=['new_chat_members'])
def initialize_chat_config(message):
    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            bot.send_message(
                message.chat.id,
                "Hello everyone! I was just added to this group."
            )
    with Session(engine) as session:
        chat = session.query(Chat).filter_by(id=message.chat.id).first()
        if not chat:
            chat = Chat(id=message.chat.id, chat_name=message.chat.title)
            chat_config = ChatConfiguration(chat_id=message.chat.id)
            session.add_all([chat, chat_config])
            session.commit()
    bot.send_message(message.chat.id, f'Initialized chat configuration with id {message.chat.id}')


@bot.message_handler(commands=['config'])
def info_chat_config(message):
    with Session(engine) as session:
        chat_config = session.query(ChatConfiguration).filter_by(chat_id=message.chat.id).first()
    msg = bot.send_message(message.chat.id, f"""To update configuration send message in this format:
    value1_name:value1
    value2_name:value2
Values available for configuration: ssh_host, ssh_port, ssh_user, ssh_password
Current configuration: 
ssh_host: {chat_config.ssh_host},
ssh_port: {chat_config.ssh_port}, 
ssh_user: {chat_config.ssh_user}, 
ssh_password: {chat_config.ssh_password}""")
    bot.register_for_reply_by_message_id(msg.id, change_chat_config)


def change_chat_config(message):
    config = message.text.split('\n')
    with Session(engine) as session:
        chat_config = session.query(ChatConfiguration).filter_by(chat_id=message.chat.id).first()
        for param in config:
            key, value = param.split(':')
            setattr(chat_config, key.strip(), value.strip())
        session.commit()
    bot.send_message(message.chat.id, f'Chat configuration updated successfully')


bot.infinity_polling()
