import configparser

config = configparser.ConfigParser()
config.read("config.ini")

acconut = config["sender"]["account"]
password = config["sender"]["password"]
smtp_server = config["sender"]["smtp_server"]
smtp_port = eval(config["sender"]["smtp_port"])

receiver_list = eval(config["receiver"]["account"])

