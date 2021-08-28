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
    #creating mpproductdepartments table for market place
    createmarketplace="CREATE TABLE `mpproductdepartments` (`id` MEDIUMINT NOT NULL AUTO_INCREMENT,\
                    `blocknumber` INT(11) NOT NULL,\
                    `txhash` VARCHAR(66) NOT NULL,\
                    `dtblockchain` DATETIME NOT NULL,\
                    `signer` VARCHAR(48) NOT NULL,\
                    `departmentid` int(11) NOT NULL,\
                    `description` VARCHAR(128) NOT NULL,PRIMARY KEY (id))"
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
        result = substrate.get_block(block_number=x)
        for extrinsic in result['extrinsics']:
            if extrinsic.address:
                signed_by_address = extrinsic.address.value
            else:
                signed_by_address = None
            if extrinsic.call_module.name=="Timestamp" and extrinsic.call.name=="set":
                currentime=extrinsic.params[0]['value']
            if extrinsic.call_module.name=="Balances" and ( extrinsic.call.name=="transfer" or extrinsic.call.name=="transfer_keep_alive"):
                ## store the transaction in the database
                store_transaction(x,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,extrinsic.params[0]['value'],extrinsic.params[1]['value'],currentime)
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
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into mpproductdepartments set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,departmentid=%s,description=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,departmentid,description)
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
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    deltx="delete from mpproductdepartments where departmentid=%s"
    datatx=(departmentid,)
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
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into mpproductcategories set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,departmentid=%s,categoryid=%s,description=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,departmentid,categoryid,description)
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
    print("Info: ",info)
    cursor = cnx.cursor()
    dtblockchain=currenttime.replace("T"," ")
    dtblockchain=dtblockchain[0:19]
    addtx="insert into mpmanufacturers set blocknumber=%s,txhash=%s,signer=%s,dtblockchain=%s,manufacturerid=%s,info=%s"
    datatx=(blocknumber,txhash,signer,dtblockchain,manufacturerid,info)
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
    cursor = cnx.cursor()
    deltx="delete from mpmanufacturers where manufacturerid=%s"
    datatx=(manufacturerid,)
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
# function to process a block of data
def process_block(blocknumber):
    # Retrieve extrinsics in block
    print("Processing Block # ",blocknumber)
    result = substrate.get_block(block_number=blocknumber)
    print ("##########################")
    print(result)
    print("Block Hash: ",result['header']['hash'])
    print ("##########################")
    events=substrate.get_events(result['header']['hash'])
    print(events)
    print ("##########################")
    cnt=0    
    for extrinsic in result['extrinsics']:
        if extrinsic.address:
            signed_by_address = extrinsic.address.value
        else:
            signed_by_address = None
        print('\nPallet: {}\nCall: {}\nSigned by: {}'.format(
            extrinsic.call_module.name,
            extrinsic.call.name,
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
        #for TimeStamp call we set the time of the following transactions
        if extrinsic.call_module.name=="Timestamp" and extrinsic.call.name=="set":
            currentime=extrinsic.params[0]['value']
        #Balance Transfer we update the transactions
        if extrinsic.call_module.name=="Balances" and ( extrinsic.call.name=="transfer" or extrinsic.call.name=="transfer_keep_alive"):
            ## store the transaction in the database
            store_transaction(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,extrinsic.params[0]['value'],extrinsic.params[1]['value'],currentime)
        #Impact Actions - Vote Approval Request
        if extrinsic.call_module.name=="ImpactActions" and extrinsic.call.name=="vote_approval_request":
            impactactions_voteapprovalrequest(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,extrinsic.params[0]['value'],extrinsic.params[1]['value'])
        #Impact Actions - Vote Approval Request
        if extrinsic.call_module.name=="ImpactActions" and extrinsic.call.name=="request_approval":
            impactactions_newapprovalrequest(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,extrinsic.params[0]['value'],extrinsic.params[1]['value'])            
        #Impact Actions - Assign Auditor to Approval Request
        if extrinsic.call_module.name=="ImpactActions" and extrinsic.call.name=="assign_auditor":
            impactactions_assignauditorapprovalrequest(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,extrinsic.params[0]['value'],extrinsic.params[1]['value'],extrinsic.params[2]['value']) 
        #Impact Actions - Remove Assigned Auditor to Approval Request
        if extrinsic.call_module.name=="ImpactActions" and extrinsic.call.name=="destroy_assigned_auditor":
            impactactions_destory_assignedauditorapprovalrequest(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,extrinsic.params[0]['value'],extrinsic.params[1]['value'])            
        # Sudo -> Impact Actions 
        if extrinsic.call_module.name=="Sudo" and extrinsic.call.name=="sudo":
            print(extrinsic.params[0].get('value'))
            c=extrinsic.params[0].get('value')
            # new impact action
            if c['call_module']== 'ImpactActions' and c['call_function']=='create_impact_action':
                print("Impact Actions - Create New Impact Action")
                print("id: ",c['call_args'][0]['value'])
                print("data: ",c['call_args'][1]['value'])
                impactactions_newimpactaction(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # destroy impact action
            if c['call_module']== 'ImpactActions' and c['call_function']=='destroy_impact_action':
                print("Impact Actions - Destroy Impact Action")
                print("id: ",c['call_args'][0]['value'])
                impactactions_destroyimpactaction(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # new oracle
            if c['call_module']== 'ImpactActions' and c['call_function']=='create_oracle':
                print("Impact Actions - Create New Oracle")
                print("id: ",c['call_args'][0]['value'])
                print("data: ",c['call_args'][1]['value'])
                impactactions_neworacle(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # destroy oracle
            if c['call_module']== 'ImpactActions' and c['call_function']=='destroy_oracle':
                print("Impact Actions - Destroy Oracle")
                print("id: ",c['call_args'][0]['value'])
                impactactions_destroyoracle(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # new auditor
            if c['call_module']== 'ImpactActions' and c['call_function']=='create_auditor':
                print("Impact Actions - Create New Auditor")
                print("id: ",c['call_args'][0]['value'])
                print("data: ",c['call_args'][1]['value'])
                impactactions_newauditor(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # destroy auditor
            if c['call_module']== 'ImpactActions' and c['call_function']=='destroy_auditor':
                print("Impact Actions - Destroy Auditor")
                print("id: ",c['call_args'][0]['value'])
                impactactions_destroyauditor(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # new proxy account
            if c['call_module']== 'ImpactActions' and c['call_function']=='create_proxy':
                print("Impact Actions - Create New Proxy")
                print("id: ",c['call_args'][0]['value'])
                print("account: ",c['call_args'][1]['value'])
                impactactions_newproxy(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # destroy proxy
            if c['call_module']== 'ImpactActions' and c['call_function']=='destroy_proxy':
                print("Impact Actions - Destroy Proxy")
                print("id: ",c['call_args'][0]['value'])
                impactactions_destroyproxy(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # new category
            if c['call_module']== 'ImpactActions' and c['call_function']=='create_category':
                print("Impact Actions - Create New Category")
                print("id: ",c['call_args'][0]['value'])
                print("description: ",c['call_args'][1]['value'])
                impactactions_newcategory(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # destroy category
            if c['call_module']== 'ImpactActions' and c['call_function']=='destroy_category':
                print("Impact Actions - Destroy Category")
                print("id: ",c['call_args'][0]['value'])
                impactactions_destroycategory(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # Market Place Create New Department
            if c['call_module']== 'MarketPlace' and c['call_function']=='create_product_department':
                print("Market Place - Create New Department")
                print("id: ",c['call_args'][0]['value'])
                print("description: ",c['call_args'][1]['value'])
                marketplace_newdepartment(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Destroy Department
            if c['call_module']== 'MarketPlace' and c['call_function']=='destroy_product_department':
                print("Market Place - Destroy Department")
                print("id: ",c['call_args'][0]['value'])
                marketplace_destroydepartment(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # Market Place Create New Category
            if c['call_module']== 'MarketPlace' and c['call_function']=='create_product_category':
                print("Market Place - Create New Category")
                print("id Department: ",c['call_args'][0]['value'])
                print("id Category: ",c['call_args'][1]['value'])
                print("Description: ",c['call_args'][2]['value'])
                marketplace_newcategory(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'],c['call_args'][2]['value'])
            # Market Place Destroy Category
            if c['call_module']== 'MarketPlace' and c['call_function']=='destroy_product_category':
                print("Market Place - Destroy Category")
                print("id Department: ",c['call_args'][0]['value'])
                print("id Category: ",c['call_args'][1]['value'])
                marketplace_destroycategory(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Create New Color
            if c['call_module']== 'MarketPlace' and c['call_function']=='create_product_color':
                print("Market Place - Create New Color")
                print("id Color: ",c['call_args'][0]['value'])
                print("Description: ",c['call_args'][1]['value'])
                marketplace_newcolor(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Destroy Color
            if c['call_module']== 'MarketPlace' and c['call_function']=='destroy_product_color':
                print("Market Place - Destroy Color")
                print("Colorid: ",c['call_args'][0]['value'])
                marketplace_destroycolor(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # Market Place Create New Size
            if c['call_module']== 'MarketPlace' and c['call_function']=='create_product_size':
                print("Market Place - Create New Size")
                print("id Size: ",c['call_args'][0]['value'])
                print("Info: ",c['call_args'][1]['value'])
                marketplace_newsize(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Destroy Size
            if c['call_module']== 'MarketPlace' and c['call_function']=='destroy_product_size':
                print("Market Place - Destroy Size")
                print("Colorid: ",c['call_args'][0]['value'])
                marketplace_destroysize(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # Market Place Create New Manufacturer
            if c['call_module']== 'MarketPlace' and c['call_function']=='create_manufacturer':
                print("Market Place - Create New Manufacturer")
                print("id Manufacturer: ",c['call_args'][0]['value'])
                print("Info: ",c['call_args'][1]['value'])
                marketplace_newmanufacturer(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Destroy Manufacturer
            if c['call_module']== 'MarketPlace' and c['call_function']=='destroy_manufacturer':
                print("Market Place - Destroy Manufacturer")
                print("Manufacturer id: ",c['call_args'][0]['value'])
                marketplace_destroymanufacturer(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # Market Place Create New Brand
            if c['call_module']== 'MarketPlace' and c['call_function']=='create_brand':
                print("Market Place - Create New Brand")
                print("id Brand: ",c['call_args'][0]['value'])
                print("Info: ",c['call_args'][1]['value'])
                marketplace_newbrand(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Destroy Brand
            if c['call_module']== 'MarketPlace' and c['call_function']=='destroy_brand':
                print("Market Place - Destroy Brand")
                print("Brand id: ",c['call_args'][0]['value'])
                marketplace_destroybrand(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
            # Market Place Create New Model
            if c['call_module']== 'MarketPlace' and c['call_function']=='create_product_model':
                print("Market Place - Create New Model")
                print("id Model: ",c['call_args'][0]['value'])
                print("Info: ",c['call_args'][1]['value'])
                marketplace_newmodel(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'],c['call_args'][1]['value'])
            # Market Place Destroy Model
            if c['call_module']== 'MarketPlace' and c['call_function']=='destroy_product_model':
                print("Market Place - Destroy Model")
                print("Model id: ",c['call_args'][0]['value'])
                marketplace_destroymodel(blocknumber,'0x'+extrinsic.extrinsic_hash,extrinsic.address.value,currentime,c['call_args'][0]['value'])
        # Loop through call params
        for param in extrinsic.params:
            if param['type'] == 'Compact<Balance>':
                param['value'] = '{} {}'.format(param['value'] / 10 ** substrate.token_decimals, substrate.token_symbol)
            print("Param '{}': {}".format(param['name'], param['value']))
        cnt=cnt+1

# subscription handler for new blocks written
def subscription_handler(obj, update_nr, subscription_id):
    print(f"New block #{obj['header']['number']} produced by {obj['author']} hash: {obj['header']['hash']}")
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
# subscribe to new block writing and process them in real time
result = substrate.subscribe_block_headers(subscription_handler, include_author=True)
print(result)


