#!/bin/bash
# This is as script to initialize some variables and launch the crawler.
# Change the variables below following your configuration, these are only examples:
export DB_NAME=aisland
export DB_USER=aisland
export DB_HOST=127.0.0.1
export DB_PWD=aszxqw1234
export NODE=ws://127.0.0.1:9944
# launching the crawler, python3 should be in the path
python3 aisland-blockchain-crawler.py $1 $2


