#!/bin/bash

curl -d "chat_id=-1001264984092&text=The market is opening in 5 minutes! Hope you have a great trading day today! :)" -X POST https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage
