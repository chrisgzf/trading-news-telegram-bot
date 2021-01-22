#!/usr/bin/env bash

kill $(pgrep -f 'python tradingbot.py')
poetry install && poetry run python tradingbot.py
