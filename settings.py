from os import getenv
data = '772380469094252554'
guild = [768748867659235348, 885910134264590347]
prefix = 'c.'
debug = False
password = getenv('PASSWORD')
username = getenv("USERNAME")
address = getenv("ADDRESS")
nodes = {
    "1":{
        "host": "ec2-34-230-43-111.compute-1.amazonaws.com",
        "port": 8080,
        "password": password,
        "name": "us-1",
        "region": "us_central"}}