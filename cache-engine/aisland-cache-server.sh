#/bin/bash
# This is as script to initialize some variable and launch the cache engine or API server.
# Change the variables below following your configuration, these are only examples:
export DB_NAME=aisland
export DB_USER=aisland
export DB_HOST=127.0.0.1
export DB_PWD=aszxqw1234
# if you want to enable TLS connection your should set this variables to your certificate and key in pem format.
#export SSL_KEY=/etc/letsencrypt/live/testnode.aisland.io/privkey.pem
#export SSL_CERT=/etc/letsencrypt/live/testnode.aisland.io/fullchain.pem
# Launching the API Server. Nodejs should be in the path
node aisland-cache-server.js



