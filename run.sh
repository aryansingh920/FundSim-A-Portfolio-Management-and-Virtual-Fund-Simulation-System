#!/bin/zsh

pip3.10 install -r requirements.txt
python3.10 main_service/main.py


kcat -b 127.0.0.1:9092 -t assets -o beginning

docker-compose down
docker-compose up -d
