# Utilities 
- Minter of AISC for Test Net
- Proxy Claim Server

# Aisland Minter for Test Net 
This programs is an https server where the user can require the transfer of 100 AISC for the TEST NET.

## Installation
- Install [Nodejs](https://nodejs.org)  
- Install the required libraries:  
```bash
npm install express
npm install readfile
npm install @polkadot/keyring
npm insall @polkadot/api
```
## Run the server:
From the command line, execute:  
```bash
node aisland-transfer-testnet.js
```
## Connect from Client:

Point the browser to your server on port 8443, for example:
https://testnet.aisland.io:8443

Insert you account and click on "Submit". 
In a few seconds you will receive 100 AISC.
