# This app listening to new blocks written read the exstrincs and store the transactions in a mysql/mariadb database.
# the database must be created, the app will create the tables and indexes used.
# import libraries
# system packages
import sys
import os
import json
# Substrate module
from substrateinterface import SubstrateInterface, Keypair
from substrateinterface.exceptions import SubstrateRequestException
# base64 encoder/decoder
import base64
# base58 encoder/decoder
import base58
#import scale library to load data types
import scalecodec
# import mysql connector
import mysql.connector
currentime=""

# read environment variables
try:
    DB_NAME=os.environ['DB_NAME']
    DB_USER=os.environ['DB_USER']
    DB_PWD=os.environ['DB_PWD']
    DB_HOST=os.environ['DB_HOST']
    NODE=os.environ['NODE']

except NameError:
    print("System Variables have not been set")
    exit(1)


# function to load data types registry
def load_type_registry_file(file_path: str) -> dict:
    with open(os.path.abspath(file_path), 'r') as fp:
        data = fp.read()
    return json.loads(data)
# function to create tables required
def create_tables():
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    cursor = cnx.cursor()
    
    # use database
    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        print(err)
        exit(1)
    # create tables
    createtx="CREATE TABLE `transactions` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,`blocknumber` INT(11) NOT NULL,`txhash` VARCHAR(66) NOT NULL,  \
                `sender` VARCHAR(64) NOT NULL,  `recipient` VARCHAR(64) NOT NULL,  `amount` numeric(32,0) NOT NULL,  \
                `dtblockchain` DATETIME NOT NULL, CONSTRAINT txhash_unique UNIQUE (txhash),PRIMARY KEY (id))"
    try:
        print("Creating table TRANSACTIONS...")
        cursor.execute(createtx)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'transactions' already exists"):
                print(err.msg)
    else:
        print("OK")
    # create indexes
    createidxtx="CREATE INDEX txhash on transactions(txhash)"
    try:
        print("Creating index TXHASH on TRANSACTIONS...")
        cursor.execute(createidxtx)
    except mysql.connector.Error as err:
            if(err.msg!="Duplicate key name 'txhash'"):
                print(err.msg)
    else:
        print("OK")
    createidxtx="CREATE INDEX sender on transactions(sender)"
    try:
        print("Creating index SENDER on TRANSACTIONS...")
        cursor.execute(createidxtx)
    except mysql.connector.Error as err:
            if(err.msg!="Duplicate key name 'sender'"):
                print(err.msg)
    else:
        print("OK")
    createidxtx="CREATE INDEX recipient on transactions(recipient)"
    try:
        print("Creating index RECIPIENT on TRANSACTIONS...")
        cursor.execute(createidxtx)
    except mysql.connector.Error as err:
        if(err.msg!="Duplicate key name 'recipient'"):
            print(err.msg)
    else:
        print("OK")
    # creating sync table to keep  syncronisation info
    createsync="CREATE TABLE `sync` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,`lastblocknumberverified` INT(11) NOT NULL, PRIMARY KEY (id))"
    try:
        print("Creating table SYNC...")
        cursor.execute(createsync)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'sync' already exists"):
                print(err.msg)
    else:
        print("OK")
    # creating categories table for impact actions
    createcategories="CREATE TABLE `impactactionscategories` (`id` MEDIUMINT NOT NULL,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `description` VARCHAR(64) NOT NULL, PRIMARY KEY (id))"
    try:
        print("Creating table impactactionscategories...")
        cursor.execute(createcategories)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'impactactionscategories' already exists"):
                print(err.msg)
    else:
        print("OK")
    # creating impactactions table for impact actions
    createactions="CREATE TABLE `impactactions` (`id` MEDIUMINT NOT NULL,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `description` VARCHAR(128) NOT NULL,\
                    `categories` VARCHAR(1024) NOT NULL,`auditors` INT(11) NOT NULL,`blockstart` INT(11) NOT NULL,\
                    `blockend` INT(11) NOT NULL, `rewardstoken` INT(11) NOT NULL, `rewardsamount` INT(32) NOT NULL,\
                    `rewardsoracle` INT(32) NOT NULL,`rewardauditors` INT(32) NOT NULL,\
                    `slashingsauditors` INT(32) NOT NULL,`maxerrorsauditor` INT(11) NOT NULL,\
                    `fields` varchar(8192) NOT NULL, \
                    PRIMARY KEY (id))"
    try:
        print("Creating table impactactions...")

        cursor.execute(createactions)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'impactactions' already exists"):
                print(err.msg)
    else:
        print("OK")
    # creating impactactionsoracles table for impact actions
    createactions="CREATE TABLE `impactactionsoracles` (`id` MEDIUMINT NOT NULL,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `description` VARCHAR(128) NOT NULL,\
                    `account` VARCHAR(48) NOT NULL,`otherinfo` VARCHAR(66) NOT NULL,\
                    PRIMARY KEY (id))"
    try:
        print("Creating table impactactionsoracles...")

        cursor.execute(createactions)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'impactactionsoracles' already exists"):
                print(err.msg)
    else:
        print("OK")
    # creating impactactionsauditors table for impact actions
    createactions="CREATE TABLE `impactactionsauditors` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                `blocknumber` INT(11) NOT NULL,\
                `txhash` VARCHAR(66) NOT NULL,\
                `dtblockchain` DATETIME NOT NULL,\
                `signer` VARCHAR(48) NOT NULL,\
                `description` VARCHAR(128) NOT NULL,\
                `account` VARCHAR(48) NOT NULL,`categories` VARCHAR(128) NOT NULL,\
                `area` VARCHAR(64) NOT NULL,`otherinfo` VARCHAR(66) NOT NULL,\
                PRIMARY KEY (id))"
    try:
        print("Creating table impactactionsauditors...")

        cursor.execute(createactions)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'impactactionsauditors' already exists"):
                print(err.msg)
    else:
        print("OK")
    # creating impactactionsproxy table for impact actions
    createactions="CREATE TABLE `impactactionsproxy` (`id` MEDIUMINT NOT NULL,\
                `blocknumber` INT(11) NOT NULL,\
                `txhash` VARCHAR(66) NOT NULL,\
                `dtblockchain` DATETIME NOT NULL,\
                `signer` VARCHAR(48) NOT NULL,\
                `account` VARCHAR(48) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table impactactionsproxy...")

        cursor.execute(createactions)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'impactactionsproxy' already exists"):
                print(err.msg)
    else:
        print("OK")
    # creating impactactionsapprovalrequests table for impact actions
    createactions="CREATE TABLE `impactactionsapprovalrequests` (`id` MEDIUMINT NOT NULL,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `info` VARCHAR(8192) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table impactactionsapprovalrequests...")

        cursor.execute(createactions)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'impactactionsapprovalrequests' already exists"):
                print(err.msg)
    else:
        print("OK")
    # creating impactactionsapprovalrequestsauditors table for impact actions
    createactions="CREATE TABLE `impactactionsapprovalrequestsauditors` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `approvalrequestid` int(11) NOT NULL,\
                    `auditor` VARCHAR(48) NOT NULL,\
                    `maxdays` INT(11) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table impactactionsapprovalrequestsauditors...")

        cursor.execute(createactions)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'impactactionsapprovalrequestsauditors' already exists"):
                print(err.msg)
    else:
        print("OK")
 # creating impactactionsapprovalrequestvotes table for impact actions
    createactions="CREATE TABLE `impactactionsapprovalrequestauditorvotes` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `approvalrequestid` int(11) NOT NULL,\
                    `vote` VARCHAR(1) NOT NULL,\
                    `otherinfo` VARCHAR(66) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table impactactionsapprovalrequestauditorvotes...")

        cursor.execute(createactions)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'impactactionsapprovalrequestauditorvotes' already exists"):
                print(err.msg)
    else:
        print("OK")
    # creating assets table for FT
    createassets="CREATE TABLE `ftassets` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `assetid` int(11) NOT NULL,\
                    `owner` VARCHAR(48) NOT NULL,\
                    `maxzombies` int(11) NOT NULL,\
                    `minbalance` int(11) NOT NULL,\
                    PRIMARY KEY (id))"
    try:
        print("Creating table ftassets...")
        cursor.execute(createassets)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'ftassets' already exists"):
                print(err.msg)
    else:
        print("OK")
    # creating transaction for fungible tokens
    createassets="CREATE TABLE `fttransactions` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `sender` VARCHAR(48) NOT NULL,\
                    `category` VARCHAR(20) NOT NULL,\
                    `assetid` int(11) NOT NULL,\
                    `recipient` VARCHAR(48) NOT NULL,\
                    `amount` int(11) NOT NULL,\
                    PRIMARY KEY (id))"
    try:
        print("Creating table fttransactions...")
        cursor.execute(createassets)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'fttransactions' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpproductdepartments table for market place
    createmarketplace="CREATE TABLE `mpproductdepartments` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `departmentid` int(11) NOT NULL,\
                    `description` VARCHAR(128) NOT NULL,\
                    `photo` VARCHAR(128) not NULL,\
                    PRIMARY KEY (id))"
    try:
        print("Creating table mpproductdepartment...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpproductdepartments' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpproductcategories table for market place
    createmarketplace="CREATE TABLE `mpproductcategories` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `departmentid` int(11) NOT NULL,\
                    `categoryid` int(11) NOT NULL,\
                    `description` VARCHAR(128) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table mpproductcategories...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpproductcategories' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpproductcolors table for the market place
    createmarketplace="CREATE TABLE `mpproductcolors` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `colorid` int(11) NOT NULL,\
                    `description` VARCHAR(128) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table mpproductcolors...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpproductcolors' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpproductsizes table for the market place
    createmarketplace="CREATE TABLE `mpproductsizes` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `sizeid` int(11) NOT NULL,\
                    `info` VARCHAR(8192) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table mpproductsizes...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpproductsizes' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpproductmodels table for the market place
    createmarketplace="CREATE TABLE `mpproductmodels` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `modelid` int(11) NOT NULL,\
                    `info` VARCHAR(8192) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table mpproductmodels...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpproductmodels' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpmanufacturers table for the market place
    createmarketplace="CREATE TABLE `mpmanufacturers` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `manufacturerid` int(11) NOT NULL,\
                    `info` VARCHAR(8192) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table mpmanufacturers...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpmanufacturers' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpbrands table for the market place
    createmarketplace="CREATE TABLE `mpbrands` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `brandid` int(11) NOT NULL,\
                    `info` VARCHAR(1024) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table mpbrands...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpbrands' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpcurrencies table for the market place
    createmarketplace="CREATE TABLE `mpcurrencies` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `currencyid` VARCHAR(8) NOT NULL,\
                    `info` VARCHAR(1024) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table mpcurrencies...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpcurrencies' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpisocuntries table for the market place
    createmarketplace="CREATE TABLE `mpisocountries` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `countryid` VARCHAR(8) NOT NULL,\
                    `name` VARCHAR(1024) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table mpisocountries...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpisocountries' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpdialcodes table for the market place
    createmarketplace="CREATE TABLE `mpdialcodes` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `countryid` VARCHAR(8) NOT NULL,\
                    `dialcode` VARCHAR(1024) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table mpdialcodes...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpdialcodes' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpshippers table for the market place
    createmarketplace="CREATE TABLE `mpshippers` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `shipperid` VARCHAR(8) NOT NULL,\
                    `info` VARCHAR(8192) NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table mpshippers...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpshippers' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpshippers table for the market place
    createmarketplace="CREATE TABLE `mpshippingrates` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `shippingratesid` VARCHAR(8) NOT NULL,\
                    `shipperid` VARCHAR(8) NOT NULL,\
                    `info` TEXT NOT NULL,PRIMARY KEY (id))"
    try:
        print("Creating table mpshippingrates...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpshippingrates' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpreviews table for the market place
    createmarketplace="CREATE TABLE `mpreviews` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `email` VARCHAR(66) NOT NULL,\
                    `productid` VARCHAR(32) NOT NULL,\
                    `stars` INT(1) NOT NULL,\
                    `thumbsup` INT(11) NOT NULL,\
                    `thumbsdown` INT(11) NOT NULL,\
                    `review` TEXT NOT NULL, \
                    PRIMARY KEY (id))"
    try:
        print("Creating table mpreviews...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpreviews' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating mpreviewsvotes table for the market place
    createmarketplace="CREATE TABLE `mpreviewsvotes` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `email` VARCHAR(66) NOT NULL,\
                    `idreview` INT(11) NOT NULL,\
                    `thumbsvote` VARCHAR(1) NOT NULL, \
                    PRIMARY KEY (id))"
    try:
        print("Creating table mpreviews...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpreviews' already exists"):
                print(err.msg)
    else:
        print("OK")
    #creating moproducts table for the market place
    createmarketplace="CREATE TABLE `mpproducts` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `email` VARCHAR(66) NOT NULL,\
                    `productid` VARCHAR(32) NOT NULL,\
                    `departmentid` INTEGER NOT NULL,\
                    `categoryid` INTEGER NOT NULL,\
                    `shortdescription` VARCHAR(64) NOT NULL,\
                    `description` TEXT NOT NULL,\
                    `specifications` TEXT NOT NULL,\
                    `photos` TEXT,\
                    `videos` TEXT,\
                    `price` numeric(36,18) NOT NULL,\
                    `currency` VARCHAR(4) NOT NULL,\
                    `upcean` VARCHAR(13),\
                    `brand` INTEGER,\
                    `model` INTEGER,\
                    `returnpolicy` INTEGER NOT NULL,\
                    `guarantee` INTEGER NOT NULL,\
                    `minimumquantity` INTEGER NOT NULL,\
                    `packagesizel` NUMERIC(8,2) NOT NULL,\
                    `packagesizeh` NUMERIC(8,2) NOT NULL,\
                    `packagesizew` NUMERIC(8,2) NOT NULL,\
                    `packageweight` NUMERIC(8,2) NOT NULL,\
                    `documents` TEXT,\
                    `info` TEXT NOT NULL,\
                     PRIMARY KEY (id))"
    try:
        print("Creating table mpproducts...")
        cursor.execute(createmarketplace)
    except mysql.connector.Error as err:
            if(err.msg!="Table 'mpproducts' already exists"):
                print(err.msg)
    else:
        print("OK")
    #regular closing of database
    cursor.close()
    cnx.close()
# function to syncronise the blockchain reading the old blocks if not yet loaded
def sync_blockchain(substrate):
    # we get the the last block from the blockchain
    r=substrate.rpc_request(method='chain_getHeader',params=[],result_handler=None)
    rs=r.get('result')
    lastblockhex=rs.get('number')
    lastblocknumber=int(lastblockhex,16)
    print("[Info] Last Block: ",lastblocknumber)
    # we check the last block reconcilied
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    cursor = cnx.cursor(dictionary=True)
    lastblocknumberverified=0
    query="select * from sync limit 1"
    try:
        cursor.execute(query)
        for row in cursor:
            lastblocknumberverified=row['lastblocknumberverified']
        #lastblocknumberverified=row.get('lastblocknumberverified')
    except mysql.connector.Error as err:
        print(err.msg)
        lastblocknumberverified=0
    
    print("[INFO] Last block number verified:",lastblocknumberverified)
    # loop the new block number to find gaps and fill them in case
    x=lastblocknumberverified+1
    cursor.close()
    cursorb = cnx.cursor()
    print("[INFO] Syncing previous blocks...")
    while x<=lastblocknumber:
        # get block data
        print("Syncing block # ",x)
        # process the block of data
        process_block(x)
        # update sync
        sqlst=""
        if(lastblocknumberverified==0):
            sqlst="insert into sync set lastblocknumberverified="+str(x)
        else:
            sqlst="update sync set lastblocknumberverified="+str(x)
        try:
            cursorb.execute(sqlst)
            cnx.commit()
        except mysql.connector.Error as err:
            print(err.msg)
            
        lastblocknumberverified=x
        # increase block number
        x=x+1
    #end while loop
    cursorb.close()
    cnx.close()



# function to store a new transaction
def store_transaction(blocknumber,txhash,sender,recipient,amount,currenttime):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Storing New Transaction")
    print("TxHash: ",txhash)
    print("Current time: ",currentime)
    print("Sender: ",sender)
    print("Recipient: ",recipient)
    print("Amount: ",amount)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into transactions set blocknumber=%s,txhash=%s,sender=%s,recipient=%s,amount=%s,dtblockchain=%s"
    datatx=(blocknumber,txhash,sender,recipient,amount,dtblockchain)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print(err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Impact Actions - New Impact Action
def impactactions_newimpactaction(blocknumber,txhash,signer,currenttime,idcategory,data):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    #decode json structure
    j=json.loads(data)
    print("Storing New Impact Action")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id: ",idcategory)
    print("Data: ",data)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into impactactions set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,id=%s"
    addtx=addtx+",description=%s,categories=%s,auditors=%s,blockstart=%s,blockend=%s,rewardstoken=%s,rewardsamount=%s,rewardsoracle=%s"
    addtx=addtx+",rewardauditors=%s,slashingsauditors=%s,maxerrorsauditor=%s,fields=%s"
    if 'fields' in j:
        f=j['fields']
    else:    
        f={}
    datatx=(blocknumber,txhash,signer,dtblockchain,idcategory,j['description'],json.dumps(j['categories']),j['auditors'],j['blockstart'],j['blockend'],j['rewardstoken'],j['rewardsamount'],j['rewardsoracle'],j['rewardsauditors'],j['slashingsauditors'],j['maxerrorsauditor'],json.dumps(f))
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()    
# function to store Impact Actions - Destroy Impact Actions
def impactactions_destroyimpactaction(blocknumber,txhash,signer,currenttime,idimpactaction):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Impact Action")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Impact Action: ",idimpactaction)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    deltx="delete from impactactions where id=%s"
    datatx=(idimpactaction,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Impact Actions - New Oracle
def impactactions_neworacle(blocknumber,txhash,signer,currenttime,idoracle,data):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    #decode json structure
    j=json.loads(data)
    print("Storing New Oracle")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id: ",idoracle)
    print("Data: ",data)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into impactactionsoracles set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,id=%s"
    addtx=addtx+",description=%s,account=%s,otherinfo=%s"
    if 'otherinfo' in j:
        o=j['otherinfo']
    else:    
        o=''
    datatx=(blocknumber,txhash,signer,dtblockchain,idoracle,j['description'],j['account'],o)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()    
# function to store Impact Actions - Destroy Oracle
def impactactions_destroyoracle(blocknumber,txhash,signer,currenttime,idoracle):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Oracle")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Oracle: ",idoracle)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    deltx="delete from impactactionsoracles where id=%s"
    datatx=(idoracle,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Impact Actions - New Approval Request
def impactactions_newapprovalrequest(blocknumber,txhash,signer,currenttime,approvalrequestid,info):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    #decode json structure
    print("Storing New Approval Request")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id: ",approvalrequestid)
    print("Info: ",info)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into impactactionsapprovalrequests set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,id=%s,info=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,approvalrequestid,info)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()   
# function to store Impact Actions - Vote Approval Request
def impactactions_voteapprovalrequest(blocknumber,txhash,signer,currenttime,approvalrequestid,data):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    j=json.loads(data)
    vote=j['vote']
    otherinfo=j['otherinfo']
    print("Storing Vote of an Approval Request")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Approval: ",approvalrequestid)
    print("Vote: ",vote)
    print("Other Info: ",otherinfo)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into impactactionsapprovalrequestauditorvotes set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,approvalrequestid=%s,vote=%s,otherinfo=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,approvalrequestid,vote,otherinfo)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close() 
# function to store Impact Actions - Assign Auditor to Approval Request
def impactactions_assignauditorapprovalrequest(blocknumber,txhash,signer,currenttime,approvalrequestid,auditor,maxdays):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    #decode json structure
    print("Storing Assigned Auditor for an Approval Request")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Approval Request Id: ",approvalrequestid)
    print("Auditor: ",auditor)
    print("Max days: ",maxdays)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into impactactionsapprovalrequestsauditors set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,approvalrequestid=%s,auditor=%s,maxdays=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,approvalrequestid,auditor,maxdays)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()   
# function to store Impact Actions - Destroy Auditor
def impactactions_destory_assignedauditorapprovalrequest(blocknumber,txhash,signer,currenttime,approvalrequestid,auditor):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Assigned Auditor to an Approval Request")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Approval Request id: ",approvalrequestid)
    print("Auditor: ",auditor)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    deltx="delete from impactactionsapprovalrequestsauditors where approvalrequestid=%s and auditor=%s"
    datatx=(approvalrequestid,auditor)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Impact Actions - New Auditor
def impactactions_newauditor(blocknumber,txhash,signer,currenttime,account,data):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    #decode json structure
    j=json.loads(data)
    print("Storing New Auditor")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Account: ",account)
    print("Data: ",data)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into impactactionsauditors set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s"
    addtx=addtx+",description=%s,account=%s,categories=%s,area=%s,otherinfo=%s"
    if 'otherinfo' in j:
        o=j['otherinfo']
    else:    
        o=''
    datatx=(blocknumber,txhash,signer,dtblockchain,j['description'],account,json.dumps(j['categories']),j['area'],o)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()    
# function to store Impact Actions - Destroy Auditor
def impactactions_destroyauditor(blocknumber,txhash,signer,currenttime,account):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Auditor")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("account: ",account)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    deltx="delete from impactactionsauditors where account=%s"
    datatx=(account,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Impact Actions - New Proxy
def impactactions_newproxy(blocknumber,txhash,signer,currenttime,idproxy, account):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Storing New Proxy")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Account: ",account)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into impactactionsproxy set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s"
    addtx=addtx+",id=%s,account=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,idproxy,account)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()    
# function to store Impact Actions - Destroy Proxy
def impactactions_destroyproxy(blocknumber,txhash,signer,currenttime,idproxy):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Proxy")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("id Proxy: ",idproxy)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    deltx="delete from impactactionsproxy where id=%s"
    datatx=(idproxy,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Impact Actions - New Category
def impactactions_newcategory(blocknumber,txhash,signer,currenttime,idcategory,description):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Storing New Category")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id category: ",idcategory)
    print("Description: ",description)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into impactactionscategories set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,id=%s,description=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,idcategory,description)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Impact Actions - Destroy Category
def impactactions_destroycategory(blocknumber,txhash,signer,currenttime,idcategory):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Category")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id category: ",idcategory)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    deltx="delete from impactactionscategories where id=%s"
    datatx=(idcategory,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to create new asset from Sudo
def assets_force_create(blocknumber,txhash,signer,currenttime,assetid,owner,maxzombies,minbalance):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Create Asset (Fungible Tokens)")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Asset Id : ",assetid)
    print("Owner : ",owner)
    print("Max Zombies : ",maxzombies)
    print("Min Balance : ",minbalance)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into ftassets set blocknumber=%s,txhash=%s,signer=%s,assetid=%s,owner=%s,maxzombies=%s,minbalance=%s,dtblockchain=%s"
    datatx=(blocknumber,txhash,signer,assetid,owner,maxzombies,minbalance,dtblockchain)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
        print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to mint assets in favor of an account
def assets_mint(blocknumber,txhash,signer,currenttime,assetid,recipient,amount):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    category="Minted"
    print("Mint Assets (Fungible Tokens)")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Asset Id : ",assetid)
    print("Recipient : ",recipient)
    print("Amount : ",amount)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into fttransactions set blocknumber=%s,txhash=%s,signer=%s,category=%s,assetid=%s,recipient=%s,amount=%s,dtblockchain=%s"
    datatx=(blocknumber,txhash,signer,category,assetid,recipient,amount,dtblockchain)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
        print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to burn assets decrease the balance of an account
def assets_burn(blocknumber,txhash,signer,currenttime,assetid,recipient,amount):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    category="Burned"
    print("Burn Assets (Fungible Tokens)")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Asset Id : ",assetid)
    print("Recipient : ",recipient)
    print("Amount : ",amount)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into fttransactions set blocknumber=%s,txhash=%s,signer=%s,category=%s,assetid=%s,recipient=%s,amount=%s,dtblockchain=%s"
    datatx=(blocknumber,txhash,signer,category,assetid,recipient,amount,dtblockchain)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
        print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to transfer assets in favor of an account
def assets_transfer(blocknumber,txhash,signer,currenttime,assetid,recipient,amount):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    category="Transfer"
    print("Mint Assets (Fungible Tokens)")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Asset Id : ",assetid)
    print("Recipient : ",recipient)
    print("Amount : ",amount)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into fttransactions set blocknumber=%s,txhash=%s,signer=%s,category=%s,assetid=%s,recipient=%s,amount=%s,dtblockchain=%s"
    datatx=(blocknumber,txhash,signer,category,assetid,recipient,amount,dtblockchain)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
        print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to force transfer assets in favor of an account
def assets_forcetransfer(blocknumber,txhash,signer,sender,currenttime,assetid,recipient,amount):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    category="Transfer"
    print("Mint Assets (Fungible Tokens)")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Asset Id : ",assetid)
    print("Recipient : ",recipient)
    print("Amount : ",amount)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into fttransactions set blocknumber=%s,txhash=%s,signer=%s,sender=%s,category=%s,assetid=%s,recipient=%s,amount=%s,dtblockchain=%s"
    datatx=(blocknumber,txhash,signer,signer,category,assetid,recipient,amount,dtblockchain)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
        print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to destroy asset (Fungible Tokens) from Sudo
def assets_force_destroy(blocknumber,txhash,signer,currenttime,assetid,witnesszombies):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Asset (Fungible Tokens)")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Asset Id: ",assetid)
    print("Witnesses Zombies: ",witnesszombies)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    deltx="delete from ftassets where assetid=%s"
    datatx=(assetid,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
        print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Market Place - New Department
def marketplace_newdepartment(blocknumber,txhash,signer,currenttime,departmentid,description):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Market Place - Storing New Department")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Department: ",departmentid)
    print("Description: ",description)
    dpid=str(departmentid)
    descriptionv=bytes.fromhex(str(description)[2:]).decode('utf-8')
    cursor = cnx.cursor()
    dtblockchain=str(currenttime).replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into mpproductdepartments set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,departmentid=%s,description=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,dpid,descriptionv)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to Destroy Product Department
def marketplace_destroydepartment(blocknumber,txhash,signer,currenttime,departmentid):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Department")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Department: ",departmentid)
    dpid=str(departmentid)
    cursor = cnx.cursor()
    dtblockchain=str(currenttime).replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    deltx="delete from mpproductdepartments where departmentid=%s"
    datatx=(dpid,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Market Place - New Category
def marketplace_newcategory(blocknumber,txhash,signer,currenttime,departmentid,categoryid,description):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Market Place - Storing New Category")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Department: ",departmentid)
    print("Id Category: ",categoryid)
    print("Description: ",description)
    dpid=str(departmentid)
    ctid=str(categoryid)
    descriptionv=bytes.fromhex(str(description)[2:]).decode('utf-8')
    cursor = cnx.cursor()
    dtblockchain=str(currenttime).replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into mpproductcategories set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,departmentid=%s,categoryid=%s,description=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,dpid,ctid,descriptionv)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to Destroy Product Category
def marketplace_destroycategory(blocknumber,txhash,signer,currenttime,departmentid,categoryid):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Category")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Department: ",departmentid)
    print("Id Category: ",categoryid)
    dpid=str(departmentid)
    ctid=str(categoryid)
    cursor = cnx.cursor()
    deltx="delete from mpproductcategories where departmentid=%s and categoryid=%s"
    datatx=(departmentid,categoryid)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Market Place - New Color
def marketplace_newcolor(blocknumber,txhash,signer,currenttime,colorid,description):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Market Place - Storing New Color")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Color: ",colorid)
    print("Description: ",description)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into mpproductcolors set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,colorid=%s,description=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,colorid,description)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to Destroy Product Category
def marketplace_destroycolor(blocknumber,txhash,signer,currenttime,colorid):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Color")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Color: ",colorid)
    cursor = cnx.cursor()
    deltx="delete from mpproductcolors where colorid=%s"
    datatx=(colorid,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Market Place - New Size
def marketplace_newsize(blocknumber,txhash,signer,currenttime,sizeid,info):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Market Place - Storing New Size")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Size: ",sizeid)
    print("Info: ",info)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into mpproductsizes set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,sizeid=%s,info=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,sizeid,info)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to Destroy Product Size
def marketplace_destroysize(blocknumber,txhash,signer,currenttime,sizeid):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Size")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Size: ",sizeid)
    cursor = cnx.cursor()
    deltx="delete from mpproductsizes where sizeid=%s"
    datatx=(sizeid,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Market Place - New Manufacturer
def marketplace_newmanufacturer(blocknumber,txhash,signer,currenttime,manufacturerid,info):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Market Place - Storing New Manufacturer")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Manufacturer: ",manufacturerid)
    print("Info: ",str(info)[2:])
    mnid=str(manufacturerid)
    infov=bytes.fromhex(str(info)[2:]).decode('utf-8')
    cursor = cnx.cursor()
    dtblockchain=str(currenttime).replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into mpmanufacturers set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,manufacturerid=%s,info=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,mnid,infov)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to Destroy Product Manufacturer
def marketplace_destroymanufacturer(blocknumber,txhash,signer,currenttime,manufacturerid):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Size")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Manufacturer: ",manufacturerid)
    mnid=str(manufacturerid)
    cursor = cnx.cursor()
    deltx="delete from mpmanufacturers where manufacturerid=%s"
    datatx=(mnid,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Market Place - New Brand
def marketplace_newbrand(blocknumber,txhash,signer,currenttime,brandid,info):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Market Place - Storing New Brand")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Brand: ",brandid)
    print("Info: ",info)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into mpbrands set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,brandid=%s,info=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,brandid,info)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to Destroy Product Brand
def marketplace_destroybrand(blocknumber,txhash,signer,currenttime,brandid):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Size")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Brand: ",brandid)
    cursor = cnx.cursor()
    deltx="delete from mpbrands where brandid=%s"
    datatx=(brandid,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Market Place - New product model
def marketplace_newmodel(blocknumber,txhash,signer,currenttime,modelid,info):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Market Place - Storing New Model")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Model: ",modelid)
    print("Info: ",info)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into mpproductmodels set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,modelid=%s,info=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,modelid,info)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to Destroy Product Model
def marketplace_destroymodel(blocknumber,txhash,signer,currenttime,modelid):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Model")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Model: ",modelid)
    cursor = cnx.cursor()
    deltx="delete from mpproductmodels where modelid=%s"
    datatx=(modelid,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Market Place - New currency
def marketplace_newcurrency(blocknumber,txhash,signer,currenttime,currencyid,info):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Market Place - Storing New Currency")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Currency: ",currencyid)
    print("Info: ",info)
    cursor = cnx.cursor()
    dtblockchain=str(currenttime).replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    currencyidv=bytes.fromhex(str(currencyid)[2:]).decode('utf-8')
    infov=bytes.fromhex(str(info)[2:]).decode('utf-8')
    addtx="insert into mpcurrencies set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,currencyid=%s,info=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,currencyidv,infov)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to Destroy Currency
def marketplace_destroycurrency(blocknumber,txhash,signer,currenttime,currencyid):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Currency")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Currency: ",currencyid)
    cursor = cnx.cursor()
    deltx="delete from mpcurrencies where currencyid=%s"
    datatx=(currencyid,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Market Place - New Country Code
def marketplace_newcountry(blocknumber,txhash,signer,currenttime,countryid,name):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Market Place - Storing New Country Code")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Country: ",countryid)
    print("Name: ",name)
    countryidv=bytes.fromhex(str(countryid)[2:]).decode('utf-8')
    namev=bytes.fromhex(str(name)[2:]).decode('utf-8')

    cursor = cnx.cursor()
    dtblockchain=str(currenttime).replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into mpisocountries set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,countryid=%s,name=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,countryidv,namev)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to Destroy Currency
def marketplace_destroycountry(blocknumber,txhash,signer,currenttime,countryid):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Country Code")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Country: ",countryid)
    cursor = cnx.cursor()
    deltx="delete from mpisocountries where countryid=%s"
    datatx=(countryid,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Market Place - New Dial Code
def marketplace_newdialcode(blocknumber,txhash,signer,currenttime,countryid,dialcode):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Market Place - Storing New Dial Code")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Country: ",countryid)
    print("Dial Code: ",dialcode)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into mpdialcodes set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,countryid=%s,dialcode=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,countryid,dialcode)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to Destroy Dial Code
def marketplace_destroydialcode(blocknumber,txhash,signer,currenttime,countryid):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Dial Code")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Country: ",countryid)
    cursor = cnx.cursor()
    deltx="delete from mpdialcodes where countryid=%s"
    datatx=(countryid,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Market Place - New Shipper
def marketplace_newshipper(blocknumber,txhash,signer,currenttime,shipperid,info):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Market Place - Storing New Shipper")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Shipper: ",shipperid)
    print("Info: ",info)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into mpshippers set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,shipperid=%s,info=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,shipperid,info)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to Destroy Shipper
def marketplace_destroyshipper(blocknumber,txhash,signer,currenttime,shipperid):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Shipper")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Shipper: ",shipperid)
    cursor = cnx.cursor()
    deltx="delete from mpshippers where shipperid=%s"
    datatx=(shipperid,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to store Market Place - New Shipping Rate
def marketplace_newshippingrates(blocknumber,txhash,signer,currenttime,shippingratesid,info):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Market Place - Storing New Shipping Rates")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Shipping Rates: ",shippingratesid)
    print("Info: ",info)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    j=json.loads(info)
    addtx="insert into mpshippingrates set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,shipperid=%s,shippingratesid=%s,info=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,j['shipperid'],shippingratesid,info)
    try:
        cursor.execute(addtx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to Destroy Shipping Rates
def marketplace_destroyshippingrates(blocknumber,txhash,signer,currenttime,shippingratesid):
    cnx = mysql.connector.connect(user=DB_USER, password=DB_PWD,host=DB_HOST,database=DB_NAME)
    print("Destroy Shipping Rates Id")
    print("BlockNumber: ",blocknumber)
    print("TxHash: ",txhash)
    print("Current time: ",currenttime)
    print("Signer: ",signer)
    print("Id Shipping Rates: ",shippingratesid)
    cursor = cnx.cursor()
    deltx="delete from mpshippingrates where shippingratesid=%s"
    datatx=(shippingratesid,)
    try:
        cursor.execute(deltx,datatx)
    except mysql.connector.Error as err:
                print("[Error] ",err.msg)
    cnx.commit()
    cursor.close()
    cnx.close()
# function to process a block of data
def process_block(blocknumber):
    # Retrieve extrinsics in block
    print("Processing Block # ",blocknumber)
    try:
        result = substrate.get_block(block_number=blocknumber)
    except Exception as e:
        print("****** WARNING IN BLOCK *****")
        print(e)
        print("******* END WARNING *********")
        return
    print ("##########################")
    print(result)
    print("Block Hash: ",result['header']['hash'])
    print ("##########################")
    events=substrate.get_events(result['header']['hash'])
    print(events)
    print ("##########################")
    cnt=0    
    for extrinsic in result['extrinsics']:
        if hasattr(extrinsic,'address'):
            signed_by_address = extrinsic.address
        else:
            signed_by_address = None
        print('\nPallet: {}\nCall: {}\nSigned by: {}'.format(
            extrinsic['call']['call_module'],
            extrinsic['call']['call_function'],
            signed_by_address
        ))
        # check for exstrinc success or not
        try:
            error=events[cnt].params[0]['value'].get('Error')
        except:
            error=None
        if events[cnt].event.name=="ExtrinsicFailed" or error!=None :
            print("Extrinsic has failed")
            cnt=cnt+1
            continue
        else:
            print("Extrinsic succeded: ",events[cnt].event.name)
        print("\n\n\nPallet: ",extrinsic['call']['call_module'])
        print("\n\n\nFunction: ",extrinsic['call']['call_function'],"\n\n\n")

        #for TimeStamp call we set the time of the following transactions
        if extrinsic['call']['call_module']['name']=="Timestamp" and extrinsic['call']['call_function']['name']=="set":
            print("extrinsic['call']['call_args']",extrinsic['call']['call_args'])
            currentime=extrinsic['call']['call_args']['now']
        #Balance Transfer we update the transactions
        if extrinsic['call']['call_module']=="Balances" and ( extrinsic['call']['call_function']=="transfer" or extrinsic['call']['call_function']=="transfer_keep_alive"):
            ## store the transaction in the database
            store_transaction(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,extrinsic.params[0]['value'],extrinsic.params[1]['value'],currentime)
        #Impact Actions - Vote Approval Request
        if extrinsic['call']['call_module']=="ImpactActions" and extrinsic['call']['call_function']=="vote_approval_request":
            impactactions_voteapprovalrequest(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,extrinsic.params[0]['value'],extrinsic.params[1]['value'])
        #Impact Actions - Vote Approval Request
        if extrinsic['call']['call_module']=="ImpactActions" and extrinsic['call']['call_function']=="request_approval":
            impactactions_newapprovalrequest(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,extrinsic.params[0]['value'],extrinsic.params[1]['value'])            
        #Impact Actions - Assign Auditor to Approval Request
        if extrinsic['call']['call_module']=="ImpactActions" and extrinsic['call']['call_function']=="assign_auditor":
            impactactions_assignauditorapprovalrequest(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,extrinsic.params[0]['value'],extrinsic.params[1]['value'],extrinsic.params[2]['value']) 
        #Impact Actions - Remove Assigned Auditor to Approval Request
        if extrinsic['call']['call_module']=="ImpactActions" and extrinsic['call']['call_function']=="destroy_assigned_auditor":
            impactactions_destory_assignedauditorapprovalrequest(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,extrinsic.params[0]['value'],extrinsic.params[1]['value'])  
        #Assets - Create new asset as regular user
        if extrinsic['call']['call_module']=="Assets" and extrinsic['call']['call_function']=="create":
            assets_force_create(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,extrinsic.params[0]['value'],extrinsic.params[1]['value'],extrinsic.params[2]['value'],extrinsic.params[3]['value'])
        #Assets - Destroy asset as regular user
        if extrinsic['call']['call_module']=="Assets" and extrinsic['call']['call_function']=="destroy":
            assets_force_destroy(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,extrinsic.params[0]['value'],extrinsic.params[1]['value'])
        #Assets - Mint assets in favor of an account
        if extrinsic['call']['call_module']=="Assets" and extrinsic['call']['call_function']=="mint":
            assets_mint(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,extrinsic.params[0]['value'],extrinsic.params[1]['value'],extrinsic.params[2]['value'])
        #Assets - Burn assets decreasing the balance of an account
        if extrinsic['call']['call_module']=="Assets" and extrinsic['call']['call_function']=="burn":
            assets_burn(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,extrinsic.params[0]['value'],extrinsic.params[1]['value'],extrinsic.params[2]['value'])
        #Assets - Transfer assets in favor of an account
        if extrinsic['call']['call_module']=="Assets" and extrinsic['call']['call_function']=="transfer":
            assets_transfer(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,extrinsic.params[0]['value'],extrinsic.params[1]['value'],extrinsic.params[2]['value'])        
        # Sudo -> Impact Actions 
        if extrinsic['call']['call_module']['name']=="Sudo" and extrinsic['call']['call_function']['name']=="sudo":
            print("*****#### SUDO")
            c=extrinsic['call']['call_args']
            nmodule=c['call']['call_module']['name']
            nfunction=c['call']['call_function']['name']
            parameters=c['call']['call_args']
            address=str(extrinsic['address'])
            extrinsic_hash=str(c['call']['call_hash'])
            # new impact action
            if nmodule== 'ImpactActions' and nfunction=='create_impact_action':
                print("Impact Actions - Create New Impact Action")
                print("id: ",c['call_args'][0]['value'])
                print("data: ",c['call_args'][1]['value'])
                impactactions_newimpactaction(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # destroy impact action
            if nmodule== 'ImpactActions' and nfunction=='destroy_impact_action':
                print("Impact Actions - Destroy Impact Action")
                print("id: ",c['call_args'][0]['value'])
                impactactions_destroyimpactaction(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # new oracle
            if nmodule== 'ImpactActions' and nfunction=='create_oracle':
                print("Impact Actions - Create New Oracle")
                print("id: ",c['call_args'][0]['value'])
                print("data: ",c['call_args'][1]['value'])
                impactactions_neworacle(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # destroy oracle
            if nmodule== 'ImpactActions' and nfunction=='destroy_oracle':
                print("Impact Actions - Destroy Oracle")
                print("id: ",c['call_args'][0]['value'])
                impactactions_destroyoracle(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # new auditor
            if nmodule== 'ImpactActions' and nfunction=='create_auditor':
                print("Impact Actions - Create New Auditor")
                print("id: ",c['call_args'][0]['value'])
                print("data: ",c['call_args'][1]['value'])
                impactactions_newauditor(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # destroy auditor
            if nmodule== 'ImpactActions' and nfunction=='destroy_auditor':
                print("Impact Actions - Destroy Auditor")
                print("id: ",c['call_args'][0]['value'])
                impactactions_destroyauditor(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # new proxy account
            if nmodule== 'ImpactActions' and nfunction=='create_proxy':
                print("Impact Actions - Create New Proxy")
                print("id: ",c['call_args'][0]['value'])
                print("account: ",c['call_args'][1]['value'])
                impactactions_newproxy(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # destroy proxy
            if nmodule== 'ImpactActions' and nfunction=='destroy_proxy':
                print("Impact Actions - Destroy Proxy")
                print("id: ",c['call_args'][0]['value'])
                impactactions_destroyproxy(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # new category
            if nmodule== 'ImpactActions' and nfunction=='create_category':
                print("Impact Actions - Create New Category")
                print("id: ",c['call_args'][0]['value'])
                print("description: ",c['call_args'][1]['value'])
                impactactions_newcategory(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # destroy category
            if nmodule== 'ImpactActions' and nfunction=='destroy_category':
                print("Impact Actions - Destroy Category")
                print("id: ",c['call_args'][0]['value'])
                impactactions_destroycategory(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # Force Create Asset
            if nmodule== 'Assets' and nfunction=='force_create':
                print("Fungibile Tokens - Create Asset")
                print("id: ",c['call_args'][0]['value'])
                print("Owner: ",c['call_args'][1]['value'])
                print("Max Zombies: ",c['call_args'][2]['value'])
                print("Minimum Deposit: ",c['call_args'][3]['value'])
                assets_force_create(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'],c['call_args'][2]['value'],c['call_args'][3]['value'])
            # Force transfer Assets
            if nmodule== 'Assets' and nfunction=='force_transfer':
                print("Fungible Tokens - Force Transfer")
                print("id: ",c['call_args'][0]['value'])
                print("Witnesses Zombies: ",c['call_args'][1]['value'])
                assets_forcetransfer(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,c['call_args'][1]['value'],currentime,c['call_args'][0]['value'],c['call_args'][2]['value'],c['call_args'][3]['value'])
            # Force Destroy Asset
            if nmodule== 'Assets' and nfunction=='force_destroy':
                print("Fungible Tokens - Create Asset")
                print("id: ",c['call_args'][0]['value'])
                print("Witnesses Zombies: ",c['call_args'][1]['value'])
                assets_force_destroy(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Create New Department
            if nmodule== 'MarketPlace' and nfunction=='create_product_department':
                print("Market Place - Create New Department")
                print("id: ",parameters['uid'])
                print("description: ",parameters['description'])
                marketplace_newdepartment(blocknumber,extrinsic_hash,address,currentime,parameters['uid'],parameters['description'])
            # Market Place Destroy Department
            if nmodule== 'MarketPlace' and nfunction=='destroy_product_department':
                print("Market Place - Destroy Department")
                print("id: ",parameters['uid'])
                marketplace_destroydepartment(blocknumber,extrinsic_hash,address,currentime,parameters['uid'])
            # Market Place Create New Category
            if nmodule== 'MarketPlace' and nfunction=='create_product_category':
                print("Market Place - Create New Category")
                print("id Department: ",parameters['uiddepartment'])
                print("id Category: ",parameters['uidcategory'])
                print("Description: ",parameters['description'])
                marketplace_newcategory(blocknumber,extrinsic_hash,address,currentime,parameters['uiddepartment'],parameters['uidcategory'],parameters['description'])
            # Market Place Destroy Category
            if nmodule== 'MarketPlace' and nfunction=='destroy_product_category':
                print("Market Place - Destroy Category")
                print("id Department: ",parameters['uiddepartment'])
                print("id Category: ",parameters['uidcategory'])
                marketplace_destroycategory(blocknumber,extrinsic_hash,address,currentime,parameters['uiddepartment'],parameters['uidcategory'])
            # Market Place Create New Color
            if nmodule== 'MarketPlace' and nfunction=='create_product_color':
                print("Market Place - Create New Color")
                print("id Color: ",c['call_args'][0]['value'])
                print("Description: ",c['call_args'][1]['value'])
                marketplace_newcolor(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Destroy Color
            if nmodule== 'MarketPlace' and nfunction=='destroy_product_color':
                print("Market Place - Destroy Color")
                print("Colorid: ",c['call_args'][0]['value'])
                marketplace_destroycolor(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # Market Place Create New Size
            if nmodule== 'MarketPlace' and nfunction=='create_product_size':
                print("Market Place - Create New Size")
                print("id Size: ",c['call_args'][0]['value'])
                print("Info: ",c['call_args'][1]['value'])
                marketplace_newsize(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Destroy Size
            if nmodule== 'MarketPlace' and nfunction=='destroy_product_size':
                print("Market Place - Destroy Size")
                print("Colorid: ",c['call_args'][0]['value'])
                marketplace_destroysize(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # Market Place Create New Manufacturer
            if nmodule== 'MarketPlace' and nfunction=='create_manufacturer':
                print("Market Place - Create New Manufacturer")
                print("id Manufacturer: ",parameters['uid'])
                print("Info: ",parameters['info'])
                marketplace_newmanufacturer(blocknumber,extrinsic_hash,address,currentime,parameters['uid'],parameters['info'])
            # Market Place Destroy Manufacturer
            if nmodule== 'MarketPlace' and nfunction=='destroy_manufacturer':
                print("Market Place - Destroy Manufacturer")
                print("Manufacturer id: ",parameters['uid'])
                marketplace_destroymanufacturer(blocknumber,extrinsic_hash,address,currentime,parameters['uid'])
            # Market Place Create New Brand
            if nmodule== 'MarketPlace' and nfunction=='create_brand':
                print("Market Place - Create New Brand")
                print("id Brand: ",c['call_args'][0]['value'])
                print("Info: ",c['call_args'][1]['value'])
                marketplace_newbrand(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Destroy Brand
            if nmodule== 'MarketPlace' and nfunction=='destroy_brand':
                print("Market Place - Destroy Brand")
                print("Brand id: ",c['call_args'][0]['value'])
                marketplace_destroybrand(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # Market Place Create New Model
            if nmodule== 'MarketPlace' and nfunction=='create_product_model':
                print("Market Place - Create New Model")
                print("id Model: ",c['call_args'][0]['value'])
                print("Info: ",c['call_args'][1]['value'])
                marketplace_newmodel(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Destroy Model
            if nmodule== 'MarketPlace' and nfunction=='destroy_product_model':
                print("Market Place - Destroy Model")
                print("Model id: ",c['call_args'][0]['value'])
                marketplace_destroymodel(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # Market Place Create New Currency
            if nmodule== 'MarketPlace' and nfunction=='create_currency':
                print("Market Place - Create New Currency")
                print("id Currency: ",parameters['currencycode'])
                print("Info: ",parameters['info'])
                marketplace_newcurrency(blocknumber,extrinsic_hash,address,currentime,parameters['currencycode'],parameters['info'])
            # Market Place Destroy Currency
            if nmodule== 'MarketPlace' and nfunction=='destroy_currency':
                print("Market Place - Destroy Currency")
                print("Currency id: ",parameters['currencycode'])
                marketplace_destroycurrency(blocknumber,extrinsic_hash,address,currentime,parameters['currencycode'])
            # Market Place Create New Country Code
            if nmodule== 'MarketPlace' and nfunction=='create_iso_country':
                print("Market Place - Create New Country Code")
                print("id Country: ",parameters['countrycode'])
                print("Name: ",parameters['countryname'])
                marketplace_newcountry(blocknumber,extrinsic_hash,address,currentime,parameters['countrycode'],parameters['countryname'])
            # Market Place Destroy Country code
            if nmodule== 'MarketPlace' and nfunction=='destroy_iso_country':
                print("Market Place - Destroy Country")
                print("Country id: ",parameters['countrycode'])
                marketplace_destroycountry(blocknumber,extrinsic_hash,address,currentime,parameters['countrycode'])
            # Market Place Create New Dial Code
            if nmodule== 'MarketPlace' and nfunction=='create_dialcode_country':
                print("Market Place - Create New Dial Code")
                print("id Country: ",c['call_args'][0]['value'])
                print("Dial Code: ",c['call_args'][1]['value'])
                marketplace_newdialcode(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Destroy Dial code
            if nmodule== 'MarketPlace' and nfunction=='destroy_dialcode_country':
                print("Market Place - Destroy Dial code")
                print("Country id: ",c['call_args'][0]['value'])
                marketplace_destroydialcode(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # Market Place Create New Shipper
            if nmodule== 'MarketPlace' and nfunction=='create_shipper':
                print("Market Place - Create New Shipper")
                print("id Shipper: ",c['call_args'][0]['value'])
                print("Info: ",c['call_args'][1]['value'])
                marketplace_newshipper(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Destroy Shipper Code
            if nmodule== 'MarketPlace' and nfunction=='destroy_shipper':
                print("Market Place - Destroy Shipper")
                print("Shipper id: ",c['call_args'][0]['value'])
                marketplace_destroyshipper(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
                 # Market Place Create New Shipper
            if nmodule== 'MarketPlace' and nfunction=='create_shipping_rates':
                print("Market Place - Create New Shipping Rate")
                print("id Shipping Rates: ",c['call_args'][0]['value'])
                print("Info: ",c['call_args'][1]['value'])
                marketplace_newshippingrates(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Destroy Shipping Rates
            if nmodule== 'MarketPlace' and nfunction=='destroy_shipping_rate':
                print("Market Place - Destroy Shipping Rates")
                print("Shipper id: ",c['call_args'][0]['value'])
                marketplace_destroyshippingrates(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
        # Loop through call params
        # print("### extrinsic['call']['call_args'] ###")
        #print(extrinsic['call']['call_args'])
        #print("### extrinsic['call']['call_args']['now'] ###")
        #print(extrinsic['call']['call_args']['now'])        
        #for param in extrinsic['call']['call_args']:
        #    print("### param ###")
        #    print(param)
        #    if param.type == 'Compact<Balance>':
        #        param.value = '{} {}'.format(param['value'] / 10 ** substrate.token_decimals, substrate.token_symbol)
        #    print("Param '{}': {}".format(param.name, paramvalue))

        cnt=cnt+1

# subscription handler for new blocks written
def subscription_handler(obj, update_nr, subscription_id):
    #print(obj)
    print(f"New block #{obj['header']['number']} produced by {obj['author']} hash: {obj['header']['parentHash']}")
    # call the block management function
    process_block(obj['header']['number'])
    
## MAIN 

# load custom data types
custom_type_registry = load_type_registry_file("../assets/types.json")
# define connection parameters
substrate = SubstrateInterface(
    url=NODE,
    ss58_format=42,
    type_registry_preset='default',
    type_registry=custom_type_registry

)
# create database tables
create_tables()
# syncronise the blockchain
if(len(sys.argv)>1):
    if (sys.argv[1]== '--sync' or sys.argv[1]=="-s"):
        sync_blockchain(substrate)
    if (sys.argv[1]== '--test' or sys.argv[1]=="-t"):
        x=32242
        process_block(x)

# subscribe to new block writing and process them in real time
result = substrate.subscribe_block_headers(subscription_handler, include_author=True)
print(result)


