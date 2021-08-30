//*********************************************************************************************
// Cache Server that offers API to query blockchain transactions by simple https calls
//*********************************************************************************************

// pulling required libraries
let express = require('express');
const https = require("https");
let fs = require('fs');
let mysql= require('mysql');

console.log("[Info] - Aisland Cache  Server - ver. 1.00 - Starting");
// read the database configuration from environment variables
const DB_HOST=process.env.DB_HOST
const DB_NAME=process.env.DB_NAME
const DB_USER=process.env.DB_USER
const DB_PWD=process.env.DB_PWD
const SSL_CERT=process.env.SSL_CERT
const SSL_KEY=process.env.SSL_KEY
// set default to local host if not set
if (typeof DB_HOST === 'undefined'){
    console.log("[Error] the environment variable DB_HOST is not set.");
    process.exit(1);
}
if (typeof DB_NAME === 'undefined'){
    console.log("[Error] the environment variable DB_NAME is not set.");
    process.exit(1);
}
// DB_USER is mandatory
if (typeof DB_USER  === 'undefined'){
    console.log("[Error] the environment variable DB_USER is not set.");
    process.exit(1);
}
// DB_PWD is mandatory
if (typeof DB_PWD === 'undefined'){
    console.log("[Error] the environment variable DB_PWD is not set.");
    process.exit(1);
}

// execute main loop as async function because of "await" requirements that cannot be execute from the main body
mainloop();
async function mainloop(){
    //setup express (http server)
    let app = express(); 
    app.use(express.urlencoded({ extended: true })); // for parsing application/x-www-form-urlencoded
    //main form in  index.html
    app.get('/',function(req,res){             
        let v=read_file("index.html");
        res.send(v);
    });
    //get transactions in the date/time limits
    app.get('/transactions',async function(req, res) {
        account=req.query.account;
        let dtstart='1990-01-01 00:00:00';
        let dtend='2999-12-31 11:59:59';
        if (typeof req.query.dts!=='undefined'){
            dtstart=req.query.dts;
        }
        if (typeof req.query.dte!=='undefined'){
            dtend=req.query.dte;
        }
        console.log("Get transactions for account:",account," from: ",dtstart," to: ",dtend);
        get_transactions(res,account,dtstart,dtend);
    });
    //get single transaction by txhash
    app.get('/transaction',async function(req, res) {
        account=req.query.account;
        let txhash='';
        if (typeof req.query.txhash!=='undefined'){
            txhash=req.query.txhash;
        }
        console.log("Get single transaction: ",txhash);
        get_transaction(res,txhash);
    });
    //get impact actions configuration
    app.get('/impactactions',async function(req, res) {
        console.log("Get Impact Action ");
        get_impactactions(res);
    });
    //get impact actions - Approval Requests
    app.get('/impactactionsapprovalrequests',async function(req, res) {
        console.log("Get Impact Action - Approval Rquests ");
        get_impactactions_approval_requests(res);
    });
    app.get('/impactactionsapprovalrequestauditorvotes',async function(req, res) {
        let id='';
        if (typeof req.query.id!=='undefined'){
            id=req.query.id;
        }
        console.log("Get Auditors' votes for an  Approval Requests: ",id);
        get_impactactions_votes_auditors(res,id);
    });
    app.get('/impactactionsapprovalrequestsauditors',async function(req, res) {
        let id='';
        if (typeof req.query.id!=='undefined'){
            id=req.query.id;
        }
        console.log("Get Auditors assigned to Approval Requests: ",id);
        get_impactactions_approval_requests_auditors(res,id);
    });
    app.get('/impactactionsapprovalrequest',async function(req, res) {
        let id='';
        if (typeof req.query.id!=='undefined'){
            id=req.query.id;
        }
        console.log("Get single transaction: ",id);
        get_impactactions_approval_request(res,id);
    });
    //get oracles in impact actions
    app.get('/impactactionsoracles',async function(req, res) {
        console.log("Get Impact Action Oracles");
        get_impactactions_oracles(res);
    });
    //get auditors in impact actions
    app.get('/impactactionsauditors',async function(req, res) {
        console.log("Get Impact Action Auditors");
        get_impactactions_auditors(res);
    });
    //get categories of impact actions
    app.get('/impactactionscategories',async function(req, res) {
        console.log("Get Impact Action Categories");
        get_impactactions_categories(res);
    });
    //get proxy accounts in impact actions
    app.get('/impactactionsproxies',async function(req, res) {
        console.log("Get Impact Action Proxies");
        get_impactactions_proxies(res);
    });
    //get assets lists (ERC20 Tokens)
    app.get('/assets',async function(req, res) {
        console.log("Get Assets List");
        get_assets(res);
    });
    //get assets transactions in the date/time limits
    app.get('/assetstransactions',async function(req, res) {
        account=req.query.account;
        assetid=req.query.assetid;
        let dtstart='1990-01-01 00:00:00';
        let dtend='2999-12-31 11:59:59';
        if (typeof req.query.dts!=='undefined'){
            dtstart=req.query.dts;
        }
        if (typeof req.query.dte!=='undefined'){
            dtend=req.query.dte;
        }
        if (typeof req.query.dte!=='undefined'){
            dtend=req.query.dte;
        }
        console.log("Get Assets transactions for account:",account," from: ",dtstart," to: ",dtend," asset id: ",assetid);
        get_assetstransactions(res,account,dtstart,dtend,assetid);
    });
    //get single transaction by txhash
    app.get('/assetstransaction',async function(req, res) {
        let txhash='';
        if (typeof req.query.txhash!=='undefined'){
            txhash=req.query.txhash;
        }
        console.log("Get single asset transaction: ",txhash);
        get_assetstransaction(res,txhash);
    });
    // listening to server port
    console.log("[Info] - Listening for HTTP connections on port TCP/3002");
    let server=app.listen(3002,function() {});
    if(typeof SSL_CERT!=='undefined' && SSL_KEY!=='undefined'){
        // loading certificate/key
        const options = {
            key: fs.readFileSync(SSL_KEY),
            cert: fs.readFileSync(SSL_CERT)
        };
        console.log("[Info] - Listening for TLS connections on port TCP/9443");
        // Https listening on port 9443 -> proxy to 3002
        https.createServer(options, app).listen(9443);
    }
}
//function to return content of a file name
function read_file(name){
    const fs = require('fs');
    if(!fs.existsSync(name))
        return(undefined);
    try {
        const data = fs.readFileSync(name, 'utf8')
        return(data);
      } catch (err) {
        console.error(err);
        return(undefined);
      }
}
// function to send transactions list in json format
async function get_transactions(res,account,dts,dte){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from transactions where (sender=? or recipient=?) and dtblockchain>=? and dtblockchain<=? order by dtblockchain,id desc";
    connection.query(
        {
            sql: sqlquery,
            values: [account,account,dts,dte]
        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Transactions not found");
                res.send('{"transactions":[]}');    
                connection.end();
                return;
            }else{
                let answer='{"transactions":[';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'{"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"sender":"'+results[r].sender+'"';
                    answer=answer+',"recipient":"'+results[r].recipient+'"';
                    answer=answer+',"amount":'+results[r].amount;
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"}';
                    x++;
                }
                answer=answer+']}';
                console.log("[Info] Sending transactions: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
// function to send single transaction  in json format
async function get_transaction(res,txhash){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from transactions where txhash=?";
    connection.query(
        {
            sql: sqlquery,
            values: [txhash]
        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Transaction not found");
                res.send('{}');    
                connection.end();
                return;
            }else{
                let answer='';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'{"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"sender":"'+results[r].sender+'"';
                    answer=answer+',"recipient":"'+results[r].recipient+'"';
                    answer=answer+',"amount":'+results[r].amount;
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"}';
                    x++;
                }
                console.log("[Info] Sending transaction: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
// function to send impact actions configuration in json format
async function get_impactactions(res){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from impactactions order by id desc";
    connection.query(
        {
            sql: sqlquery,
        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Impact Actions not found");
                res.send('{"proxies":[]}');    
                connection.end();
                return;
            }else{
                let answer='{"impactactions":[';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'{"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"sender":"'+results[r].signer+'"';
                    answer=answer+',"description":"'+results[r].description+'"';
                    answer=answer+',"categories":'+results[r].categories;
                    answer=answer+',"auditors":'+results[r].auditors;
                    answer=answer+',"blockstart":'+results[r].blockstart;
                    answer=answer+',"blockend":'+results[r].blockend;
                    answer=answer+',"rewardstoken":'+results[r].rewardstoken;
                    answer=answer+',"rewardsamount":'+results[r].rewardsamount;
                    answer=answer+',"rewardsoracle":'+results[r].rewardsoracle;
                    answer=answer+',"rewardauditors":'+results[r].rewardauditors;
                    answer=answer+',"slashingsauditors":'+results[r].slashingsauditors;
                    answer=answer+',"maxerrorsauditor":'+results[r].maxerrorsauditor;
                    answer=answer+',"fields":'+results[r].fields;
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"}';
                    x++;
                }
                answer=answer+']}';
                console.log("[Info] Sending Impact Actions: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
// function to send impact actions - approval requests in json format
async function get_impactactions_approval_requests(res){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from impactactionsapprovalrequests order by id desc";
    connection.query(
        {
            sql: sqlquery,
        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Impact Actions - Approval requests not found");
                res.send('{"approvalrequests":[]}');    
                connection.end();
                return;
            }else{
                let answer='{"approvalrequests":[';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'{"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"signer":"'+results[r].signer+'"';
                    answer=answer+',"info":'+results[r].info;
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"}';
                    x++;
                }
                answer=answer+']}';
                console.log("[Info] Sending Impact Actions - Approval Requests: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
// function to send impact actions - auditors assigned to approval requests in json format
async function get_impactactions_approval_requests_auditors(res,id){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from impactactionsapprovalrequestsauditors where approvalrequestid=? order by id desc";
    connection.query(
        {
            sql: sqlquery,
            values: [id]

        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Impact Actions - Auditor assigned to Approval requests not found");
                res.send('{"approvalrequestsauditors":[]}');    
                connection.end();
                return;
            }else{
                let answer='{"approvalrequestsauditors":[';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'{"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"signer":"'+results[r].signer+'"';
                    answer=answer+',"approvalrequestid":'+results[r].approvalrequestid;
                    answer=answer+',"auditor":"'+results[r].auditor+'"';
                    answer=answer+',"maxdays":'+results[r].maxdays;
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"}';
                    x++;
                }
                answer=answer+']}';
                console.log("[Info] Sending Impact Actions - Auditors assignet to Approval Requests: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
// function to send impact actions - votes's auditors for an approval requests in json format
async function get_impactactions_votes_auditors(res,id){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from impactactionsapprovalrequestauditorvotes where approvalrequestid=? order by id desc";
    connection.query(
        {
            sql: sqlquery,
            values: [id]

        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Impact Actions - Auditors' Votes for an  Approval requests not found");
                res.send('{"approvalrequestsauditors":[]}');    
                connection.end();
                return;
            }else{
                let answer='{"approvalrequestsauditorsvotes":[';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'{"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"signer":"'+results[r].signer+'"';
                    answer=answer+',"approvalrequestid":'+results[r].approvalrequestid;
                    answer=answer+',"vote":"'+results[r].auditor+'"';
                    answer=answer+',"otherinfo":"'+results[r].otherinfo+'"';
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"}';
                    x++;
                }
                answer=answer+']}';
                console.log("[Info] Sending Impact Actions - Auditors's votes for an Approval Requests: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
// function to send a single impact action in json format
async function get_impactactions_approval_request(res,id){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from impactactionsapprovalrequests where id=?";
    connection.query(
        {
            sql: sqlquery,
            values: [id]
        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Impact Actions - Approval request not found");
                res.send('{}');    
                connection.end();
                return;
            }else{
                let answer='{';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"signer":"'+results[r].signer+'"';
                    answer=answer+',"info":'+results[r].info;
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"';
                    x++;
                }
                answer=answer+'}';
                console.log("[Info] Sending Impact Actions - Single Approval Request: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
// function to send impact actions/auditors list in json format
async function get_impactactions_auditors(res){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from impactactionsauditors order by id desc";
    connection.query(
        {
            sql: sqlquery,
        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Impact Actions Auditors not found");
                res.send('{"auditors":[]}');    
                connection.end();
                return;
            }else{
                let answer='{"auditors":[';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'{"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"sender":"'+results[r].signer+'"';
                    answer=answer+',"description":"'+results[r].description+'"';
                    answer=answer+',"account":"'+results[r].account+'"';
                    answer=answer+',"categories":'+results[r].categories;
                    answer=answer+',"area":'+results[r].area;
                    answer=answer+',"otherinfo":"'+results[r].otherinfo+'"';
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"}';
                    x++;
                }
                answer=answer+']}';
                console.log("[Info] Sending Impact Actions Auditors: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
// function to send impact actions/oracles list in json format
async function get_impactactions_oracles(res){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from impactactionsoracles order by id desc";
    connection.query(
        {
            sql: sqlquery,
        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Impact Actions Oracles not found");
                res.send('{"oracles":[]}');    
                connection.end();
                return;
            }else{
                let answer='{"oracles":[';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'{"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"sender":"'+results[r].signer+'"';
                    answer=answer+',"account":"'+results[r].account+'"';
                    answer=answer+',"otherinfo":"'+results[r].otherinfo+'"';
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"}';
                    x++;
                }
                answer=answer+']}';
                console.log("[Info] Sending Impact Actions Oracles: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
// function to send impact actions/proxies list in json format
async function get_impactactions_proxies(res){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from impactactionsproxy order by id desc";
    connection.query(
        {
            sql: sqlquery,
        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Impact Actions Proxies not found");
                res.send('{"proxies":[]}');    
                connection.end();
                return;
            }else{
                let answer='{"proxies":[';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'{"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"sender":"'+results[r].signer+'"';
                    answer=answer+',"account":"'+results[r].account+'"';
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"}';
                    x++;
                }
                answer=answer+']}';
                console.log("[Info] Sending Impact Actions Proxies: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
// function to send impact actions/categories list in json format
async function get_impactactions_categories(res){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from impactactionscategories order by id";
    connection.query(
        {
            sql: sqlquery,
        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Impact Actions Categories not found");
                res.send('{"categories":[]}');    
                connection.end();
                return;
            }else{
                let answer='{"categories":[';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'{"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"sender":"'+results[r].signer+'"';
                    answer=answer+',"description":"'+results[r].description+'"';
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"}';
                    x++;
                }
                answer=answer+']}';
                console.log("[Info] Sending Impact Actions Categories: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
// function to send impact actions configuration in json format
async function get_assets(res){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from ftassets order by id desc";
    connection.query(
        {
            sql: sqlquery,
        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Assets not found");
                res.send('{"assets":[]}');    
                connection.end();
                return;
            }else{
                let answer='{"assets":[';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'{"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"signer":"'+results[r].signer+'"';
                    answer=answer+',"assetid":"'+results[r].assetid+'"';
                    answer=answer+',"owner":"'+results[r].owner+'"';
                    answer=answer+',"maxzombies":'+results[r].maxzombies;
                    answer=answer+',"minbalance":'+results[r].minbalance;
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"}';
                    x++;
                }
                answer=answer+']}';
                console.log("[Info] Sending Assets: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
// function to send transactions list in json format
async function get_assetstransactions(res,account,dts,dte,assetid){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from fttransactions where (sender=? or recipient=?) and dtblockchain>=? and dtblockchain<=? and assetid=? order by dtblockchain,id desc";
    connection.query(
        {
            sql: sqlquery,
            values: [account,account,dts,dte,assetid]
        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Assets Transactions not found");
                res.send('{"assetstransactions":[]}');    
                connection.end();
                return;
            }else{
                let answer='{"assetstransactions":[';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'{"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"signer":"'+results[r].signer+'"';
                    answer=answer+',"sender":"'+results[r].sender+'"';
                    answer=answer+',"recipient":"'+results[r].recipient+'"';
                    answer=answer+',"assetid":"'+results[r].assetid+'"';
                    answer=answer+',"category":"'+results[r].category+'"';
                    answer=answer+',"amount":'+results[r].amount;
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"}';
                    x++;
                }
                answer=answer+']}';
                console.log("[Info] Sending Assets transactions: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
// function to send single transaction  in json format
async function get_assetstransaction(res,txhash){
    let connection = mysql.createConnection({
        host     : DB_HOST,
        user     : DB_USER,
        password : DB_PWD,
        database : DB_NAME
    });
    sqlquery="select * from fttransactions where txhash=?";
    connection.query(
        {
            sql: sqlquery,
            values: [txhash]
        },
        function (error, results, fields) {
            if (error){
                console.log("[Error]"+error);
                throw error;
            }
            if(results.length==0){
                console.log("[Debug] Transaction not found");
                res.send('{}');    
                connection.end();
                return;
            }else{
                let answer='';
                let x=0;
                for (r in results) {
                    if(x>0){
                        answer=answer+',';
                    }
                    answer= answer+'{"id":'+results[r].id;
                    answer=answer+',"blocknumber":'+results[r].blocknumber+',"txhash":"'+results[r].txhash+'"';
                    answer=answer+',"signer":"'+results[r].signer+'"';
                    answer=answer+',"sender":"'+results[r].sender+'"';
                    answer=answer+',"recipient":"'+results[r].recipient+'"';
                    answer=answer+',"assetid":"'+results[r].assetid+'"';
                    answer=answer+',"category":"'+results[r].category+'"';
                    answer=answer+',"amount":'+results[r].amount;
                    answer=answer+',"dtblockchain":"'+results[r].dtblockchain+'"}';
                    x++;
                }
                console.log("[Info] Sending transaction: ",answer);
                res.send(answer);
                connection.end();
                return;
            }
        }
    );
}
