#!/bin/bash

curl -d "chat_id=-1001264984092&text=The market has closed. Hope you had a great trading day today! :)" -X POST https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage
