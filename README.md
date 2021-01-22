# Trading News Bot

To use `marketclose.sh` and `marketopen.sh`, add these to crontab

```
25 22 * * 1-5   /home/chris/marketopen.sh
0 5 * * 2-6     /home/chris/marketclose.sh
```

You will need to export your telegram bot token to `$TELEGRAM_TOKEN`.
