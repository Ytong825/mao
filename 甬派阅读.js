// 当前脚本来自于 http://script.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cc 脚本库下载！
// 脚本库官方QQ群1群: 429274456
// 脚本库官方QQ群2群: 1077801222
// 脚本库官方QQ群3群: 433030897
// 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
// 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
// 您在使用脚本库下载的脚本时自行检查判断风险。
// 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。

/*
环境变量yongpai
多账户换行
需要手动抓一个wtoken值
账号1#密码1#支付宝姓名1#支付宝账号1#设备id1
*/
const $ = Env('甬派转盘')
const notify = require('./sendNotify')
const moment = require('moment');
const { HttpsProxyAgent } = require('hpagent')
const got = require('got')
const fs = require('fs');
const envSplitor = ['\n']     //支持多种分割，但要保证变量里不存在这个字符
const ckNames = ['yongpai']      //支持多变量
//=======================================================================================================
const DEFAULT_RETRY = 1           // 默认重试次数
let MODE = 0                    // 并发控制 1-并发  0-顺序

// =============================================== 代理api ========================================================
let Proxy_url = ''             
//=======================内置wtoken=================================================================================
let wtoken = ''// 手动抓wtoken可1带10


async function FinalTask(){
    await $.UserCycle(async(user) =>{
        $.log(`\n\n====================  ${user.idx}  ====================`)
        await user.init();
        await user.UserTasks()
    })
    // MODE = 1
    // //$.log('开宝箱', { sp: true, console: false })  // 带分割的打印
    // await $.UserThread('Thread',{taskName:'getip',thread:3,opt:[]})
    // await $.UserThread(async(user) =>{
    // })
}
class UserClass {
    constructor(ck) {
        this.idx = `账号[${++$.userIdx}]: `
        
        this.phone = ck.split("#")[0]
        this.password = ck.split("#")[1]
        this.realname = ck.split("#")[2]
        this.aliPay = ck.split("#")[3]
        this.deviceId = ck.split("#")[4]
        this.x_token = ck.split("#")[5]
        this.needLogin = true;
        
        this.user=$.userIdx
        this.Cycle = ({taskName,thread,opt=[]}) => $.TaskCycle(this[taskName].bind(this),thread,...Object.values(opt))
        this.Thread = ({taskName,thread,opt=[]}) => $.TaskThread(this[taskName].bind(this),thread,...Object.values(opt))
    }

    async init() {
        if (this.needLogin) {
            await this.loginPwdGet();
            this.needLogin = false;
        }
        return this;
    }

    async loginPwdGet() {
        let options = {  
            fn: '登陆',
            method: 'get',
            url: `https://ypapp.cnnb.com.cn/yongpai-user/api/login2/local3?username=${this.phone}&password=${encodeURI(this.password)}&deviceId=${this.deviceId}&globalDatetime=${Date.now()}&sign=${MD5(`globalDatetime${Date.now()}username${this.phone}test_123456679890123456`).toUpperCase()}`,
            headers : {
                'system': 'android',
                'version': '29',
                'model': "MI 8",
                'appversion': '11.3.2',
                'appbuild': '202504020',
                'deviceid': this.deviceId,
                'ticket': '',
                'accept-encoding': 'gzip',
                'user-agent': 'okhttp/4.9.1',
            },
        }
        try {
            let { resp } = await $.request(options)
            //console.log(JSON.stringify(resp))
            await $.wait($.randomInt(1, 2))
            if (resp.data?.userId && resp.data?.token) {
                this.userId = resp.data.userId
                this.sessionId = resp.data.token
                this.log(`登录成功：${this.phone.replace(/(\d{3})\d*(\d{3})/, '$1****$2')}`);
            } else {
                this.log(`登录失败：返回数据不完整 ${JSON.stringify(resp)}`);
                throw new Error("登录返回参数缺失");
            }
        } catch (e) {
            this.log(`登录异常：${e.message}`);
            throw e; // 抛出异常，让上层感知登录失败
        }
    } 


    async frontPage(Authorization) {
        let options = {  
            fn: '打开页面',
            method: 'get',
            url: `https://act.tmlyun.com/activity-api/lottery/h5/activity/lottery/frontPage?activityId=${this.activityId}&clientId=${this.deviceId}`,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 12; NOH-AN00 Build/HUAWEINOH-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.34 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
                'Authorization': Authorization
            }
        }
            let { resp } = await $.request(options)
            // console.log(JSON.stringify(resp))
    
            if (resp.code==0) {
                this.log(`${options.fn}：${resp.message}`)
            } else{
                this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
            }
            await $.wait($.randomInt(1, 2))
    }  




    async UserTasks() {
        if (!this.userId || !this.sessionId) {
            this.log("未登录，无法执行任务", { sp: true });
            return;
        }

        //  if(this.user==2){}else{return}
        //this.log('开宝箱', { sp: true, console: false })  // 带分割的打印
        // await this.Thread({taskName:'getip',thread:3})
         await this.client()

        this.log('抽奖', { sp: true, console: false })  // 带分割的打印
        let au = await this.userLogin({q:'1DvvL80TsnkfuVjfbdhTeOa1Xz0ttq5tQkt33EX3Kvc=',"tenantCode": "yongpai"},'https://act.tmlyun.com/activity-api/lottery/api/auth/userLogin')
        if(au){
            // this.log(au)
            await this.frontPage(au)
            await this.userActivityLottery(au)
            await this.userIntegralInfo(au)
            await this.userPrizeRecord(au)
        }
    }

async userLogin(id,url) {
    let options = {  
        fn: '获取token',
        method: 'post',
        url: url,
        headers: {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; NOH-AN00 Build/HUAWEINOH-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.34 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai'
        },
        json:Object.assign({
            "accountId": this.userId,
            "sessionId": this.sessionId,
            
        },id)
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))
        await $.wait($.randomInt(1, 2))
        if (resp.code==0) {
            this.log(`${options.fn}：${resp.message}`)
            if(resp.data?.thirdId){this.activityId = resp.data.thirdId}
            return resp.data.token
        } else{
            this.log(`${options.fn}： ${JSON.stringify(resp)}`)
            return null
        }
        
} 
async frontPage(Authorization) {
    let options = {  
        fn: '打开页面',
        method: 'get',
        url: `https://act.tmlyun.com/activity-api/lottery/h5/activity/lottery/frontPage?activityId=${this.activityId}&clientId=${this.deviceId}`,
        headers: {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; NOH-AN00 Build/HUAWEINOH-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.34 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
            'Authorization': Authorization
        }
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))

        if (resp.code==0) {
            this.log(`${options.fn}：${resp.message}`)
        } else{
            this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
        }
        await $.wait($.randomInt(1, 2))
}  

async saveActivityUserInfo(Authorization) {
    let options = {   
        fn: '抽奖登记手机号',
        method: 'post',
        url: `https://act.tmlyun.com/activity-api/lottery/h5/activity/lottery/saveActivityUserInfo`,
        headers: {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; NOH-AN00 Build/HUAWEINOH-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.34 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
            'Authorization': Authorization
        },
        json:{
            "activityUserName": "先生",
            "activityUserTel": this.phone+'',
            "activityId": Number(this.activityId),
            "clientId": this.deviceId
        }
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))

        if (resp.code==0) {
            this.log(`${options.fn}：${resp.message}`)
        } else{
            this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
        }
        await $.wait($.randomInt(1, 2))
} 
async userActivityLottery(Authorization) {
    let options = { 
        fn: '抽奖',
        method: 'post',
        url: `https://act.tmlyun.com/activity-api/lottery/h5/activity/lottery/userActivityLottery`,
        headers: {
            'User-Agent':'Mozilla/5.0 (Linux; Android 12; NOH-AN00 Build/HUAWEINOH-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.34 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
            'Authorization': Authorization,
            'X-REQUEST-ID': '',
        },
        json:{
            "activityId": this.activityId,
            "clientId": this.deviceId,
            "prizeVersion": 0,
            "token": ""
        }
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))
        if(JSON.stringify(resp).includes('用户信息未填写')){
            this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
            await this.saveActivityUserInfo(Authorization)
            await this.userActivityLottery(Authorization)
        }else if (resp.code==0) {
            this.log(`${options.fn}：${resp.data?.isPrize == 0 ? '谢谢参与':`获得 🧧${resp.data.grade}🧧`}`)
        } else{
            this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
        }
        await $.wait($.randomInt(1, 2))
}
async userExchangeIntegral(Authorization) {
    let options = { 
        fn: '兑换抽奖次数',
        method: 'get',
        url: `https://act.tmlyun.com/activity-api/lottery/h5/activity/lottery/userExchangeIntegral?activityId=${this.activityId}`,
        headers: {
            'User-Agent':'Mozilla/5.0 (Linux; Android 12; NOH-AN00 Build/HUAWEINOH-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.34 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
            'Authorization': Authorization,
        }
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))
        if (resp.code==0) {
            this.log(`${options.fn}：${resp.message}，消耗 ${resp.data.integralExchangeNum} 积分`)
            await this.userActivityLottery(Authorization)
        } else{
            this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
        }
        await $.wait($.randomInt(1, 2))
}
async userIntegralInfo(Authorization) {
    let options = { 
        fn: '可兑换次数',
        method: 'get',
        url: `https://act.tmlyun.com/activity-api/lottery/h5/activity/lottery/userIntegralInfo?activityId=${this.activityId}`,
        headers: {
            'User-Agent':'Mozilla/5.0 (Linux; Android 12; NOH-AN00 Build/HUAWEINOH-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.34 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
            'Authorization': Authorization,
        }
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))
        if (resp.code==0) {
            this.log(`${options.fn}：${resp.data.exchangeNum} 次，积分余额：${resp.data.remainIntegral} `)
            if(resp.data.exchangeNum > 0){
                await this.userExchangeIntegral(Authorization)
            }
        } else{
            this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
        }
        await $.wait($.randomInt(1, 2))
}
async userPrizeRecord(Authorization) {
    let options = {    
        fn: '奖品列表',
        method: 'get',
        url: `https://act.tmlyun.com/activity-api/lottery/h5/activity/lottery/accountPrizeRecord/userPrizeRecord?activityId=${this.activityId}`,
        headers: {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; NOH-AN00 Build/HUAWEINOH-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.34 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
            'Authorization': Authorization
        }
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))

        if (resp.code==0) {
            if(resp.data.activityAccountPrizeVoList.length >0){
                let login_u = decodeURIComponent(resp.data.activityAccountPrizeVoList[0].quanDetailYiLink).split('u=')[1]
                let txau = await this.userLogin({u:login_u},'https://my.tmlyun.com/equity-api/user/auth/userLogin')
                await this.getFundsDetail(txau)
            }
            //this.log(`${options.fn}：${resp.data.activityAccountPrizeVoList.length >0 ? resp.data.activityAccountPrizeVoList.map(x => `[${x.grade}]`).join('--') : '奖品为空'}`)
        } else{
            this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
        }
        await $.wait($.randomInt(1, 2))
}
async getFundsDetail(Authorization) {
    let options = {   
        fn: '提现信息',
        method: 'get',
        url: `https://my.tmlyun.com/equity-api/redBag/getFundsDetail?fundsChannelType=0`,
        headers: {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; NOH-AN00 Build/HUAWEINOH-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.34 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
            'Authorization': Authorization
        }
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))

        if (resp.code==0) {
                this.log(`${options.fn}：${$.phoneNum(resp.data.account)}，可提现：${resp.data.price}`)
                if(resp.data.account ==''){
                    await this.saveAliPayAccount(Authorization,this.aliPay,this.realname)
                    }else if(resp.data.price>0){
                        await this.createTrans(Authorization,resp.data.price)
                    }
        } else{
            this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
        }
        await $.wait($.randomInt(1, 2))
}
async saveAliPayAccount(Authorization,aliPay,name) {
    let options = {
        fn: '绑定支付宝',
        method: 'get',
        url: `https://my.tmlyun.com/equity-api/redBag/saveAliPayAccount?userName=${encodeURIComponent(name)}&account=${aliPay}`,
        headers: {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; NOH-AN00 Build/HUAWEINOH-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.34 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
            'Authorization': Authorization
        }
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))

        if (resp.code==0) {
            this.log(`${options.fn}：${resp.message}`)
        } else{
            this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
        }
        await $.wait($.randomInt(1, 2))
}
async createTrans(Authorization,price) {
    let options = {    
        fn: '提现',
        method: 'get',
        url: `https://my.tmlyun.com/equity-api/redBag/createTrans?price=${price}&fundsChannelType=0&yToken=&deviceId=${this.deviceId}`,
        headers: {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; NOH-AN00 Build/HUAWEINOH-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.34 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
            'Authorization': Authorization
        }
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))

        if (resp.code==0) {
            this.log(`${options.fn}：${resp.message}`)
        } else{
            this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
        }
        await $.wait($.randomInt(1, 2))
}
async newlist() {
    let options = {    
        fn: '获取文章',
        method: 'get',
        url: `https://ypapp.cnnb.com.cn/yongpai-news/api/v2/news/list?channelId=0&currentPage=1&timestamp=${new Date().getTime()}`,
        headers: {
        }
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))

        if (resp.code==0) {
            // this.log(`${options.fn}：${resp.message}`)
            for(let x of resp.data.content){
                await this.detail(x.newsId)
                await this.TYyd('阅读', x, `https://ypapp.cnnb.com.cn/yongpai-news/api/news/detail?newsId=${x.newsId}&userId=${this.userId}`)
                await this.TYyd('点赞', x, `https://ypapp.cnnb.com.cn/yongpai-ugc/api/praise/save_news?deviceId=${this.deviceId}&newsId=${x.newsId}&userId=${this.userId}`)
                await this.TYyd('分享', x, `https://ypapp.cnnb.com.cn/yongpai-ugc/api/forward/news?newsId=${x.newsId}&source=4&userId=${this.userId}`)
                // return
            }
        } else{
            this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
        }
        await $.wait($.randomInt(1, 2))
}
async detail(newsId) {
    let options = {    
        fn: '打开文章',
        method: 'post',
        url: `https://ypapp.cnnb.com.cn/yongpai-user/api/daily/news/detail`,
        headers: {
            'content-type':'application/json; charset=UTF-8'
        },
        json:{"access":1,"brand":"HUAWEI","call_type":0,"carrier":"中国电信","channel_id":"27","device_id":this.deviceId,"device_model":"NOH-AN00","duration":0,"news_id":newsId,"os":"Android","os_version":"12","record_ts":new Date().getTime(),"uid":this.userId}
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))

        if (resp.code==0) {
            // this.log(`${options.fn}：${resp.message}`)
        } else{
            this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
        }
        await $.wait($.randomInt(1, 2))
}
async TYyd(fn,list,url) {
    let options = {    
        fn: fn,
        method: 'get',
        url: url,
        headers: {
            "appversion": `12.0.8`,
            "deviceid": this.deviceId,
            'system': 'Android',
            'version': '31',
            'model': 'NOH-AN00',
            'appbuild': '202512180',
            'wtoken': wtoken,
            'user-agent': 'okhttp/4.9.1'
        }
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))

        if (resp.message == 'OK') {
            this.log(`${options.fn}[${list.title}]：✅`)
        } else{
            this.log(`${options.fn}[${list.title}]：❌`)
        }
        await $.wait($.randomInt(1, 2))
}
async client() {
    let options = {    
        fn: '积分余额',
        method: 'get',
        url: `https://ypapp.cnnb.com.cn/yongpai-user/api/user/client?userId=${this.userId}&deviceId=${this.deviceId}&token=${this.sessionId}`,
        headers: {
        }
    }
        let { resp } = await $.request(options)
        // console.log(JSON.stringify(resp))

        if (resp.code==0) {
            this.log(`${options.fn}：${resp.data.score}`)
            if(resp.data.score<150){
                await this.newlist()
            }
        } else{
            this.log(`${options.fn}： ${resp?.message? resp.message : JSON.stringify(resp)}`)
        }
        await $.wait($.randomInt(1, 2))
}



log(msg, options = {}){
    if(MODE){$.log(this.idx+msg, options)}else{$.log(msg, options)}
} 

}
!(async () => {
    // console.log(await $.yiyan())
    $.read_env(UserClass)
    await FinalTask()

})()
    .catch((e) => $.log(e, { notify: false }))
    .finally(() => $.exitNow())



  
//=============================================================== 
function Env(name) {
    return new class {
        constructor(name) {
            this.name = name
            this.startTime = Date.now()
            this.log(`[${this.name}]开始运行`, { time: true })
            this.notifyStr = []
            this.notifyFlag = true
            this.ip = '';
            this.userIdx = 0
            this.userList = []
            this.userCount = 0
        }
        async request(opt) {
            if(opt.Proxy&&typeof opt.Proxy == 'boolean'){opt.Proxy = {url:Proxy_url}}
            if(opt.ip){opt.ip[0] =''}
            let DEFAULT_TIMEOUT = 80000      // 默认超时时间
            let resp = null, count = 0, nextip = 0
            let fn = opt.fn || opt.url
            opt.timeout = opt.timeout || DEFAULT_TIMEOUT
            opt.retry = opt.retry || { limit: 0 }
            opt.method = opt?.method?.toUpperCase() || 'GET'
            // opt['followRedirect'] = true
            opt['throwHttpErrors'] = false  
            // opt['decompress'] = false  
            while (nextip++ < 10){
                if((opt?.Proxy?.reset||this.ip =='')&&opt?.Proxy?.url){
                    this.ip = (await got(opt.Proxy.url)).body
                    this.log(this.ip);
                    }
                while (count++ < DEFAULT_RETRY) {
                    const promiseTimeout = new Promise((resolve, reject) => {
                            let wait = setTimeout(() => {
                                clearTimeout(wait);
                                reject('Request timed out');
                            }, opt.timeout);
                        }); 
                    try {
                        if(opt?.Proxy?.url){opt['agent'] = { https: new HttpsProxyAgent({keepAlive: true,keepAliveMsecs: opt.timeout,proxy: `http://${this.ip}`})}}
                        resp = await Promise.race([got(opt),promiseTimeout])
                        break
                    } catch (e) {
                        try { e = JSON.parse(e) } catch { }
                        if (e.name == 'TimeoutError'||e == 'Request timed out') {
                            this.log(`[${fn}]请求超时，重试第${count}次${e == 'Request timed out'?'，超时强制中断':''}`)
                        } else {
                            this.log(`[${fn}]请求错误：重试第${count}次`)//${JSON.stringify(e)}，
                        }
                    }
                }
                if (resp !== null || !opt?.Proxy) break
                count = 0
                if(opt?.Proxy?.url){
                    this.ip = (await got(opt.Proxy.url)).body
                    this.log(this.ip);
                    opt['agent'] = { https: new HttpsProxyAgent({keepAlive: true,keepAliveMsecs: opt.timeout,proxy: `http://${this.ip}`})}
                }
            }
            if (resp == null) return Promise.resolve({ resp: null, hd: null, code: 'timeout' })
            let { statusCode, headers, body } = resp
            try { body = JSON.parse(body) } catch { }
            try { headers = JSON.parse(headers) } catch { }
            return Promise.resolve({ resp:body, hd:headers, code:statusCode });
        }

        log(msg, options = {}) {
            let opt = { console: true }
            Object.assign(opt, options)
            if (opt.time) {
                let fmt = opt.fmt || 'hh:mm:ss'
                msg = `[${this.time(fmt)}]` + msg
            }
            if (opt.notify) {
                this.notifyStr.push(msg)
            }
            if (opt.console) {
                console.log(msg)
            }
            if (opt.sp) {
                console.log(`\n-------------- ${msg} --------------`)
            }
        }
        read_env(Class) {
            let envStrList = ckNames.map(x => process.env[x])
            
            for (let env_str of envStrList.filter(x => !!x)) {
                let sp = envSplitor.filter(x => env_str.includes(x))
                let splitor = sp.length > 0 ? sp[0] : envSplitor[0]
                for (let ck of env_str.split(splitor).filter(x => !!x)) {
                    this.userList.push(new Class(ck))
                }
            }
            this.userCount = this.userList.length
            if (!this.userCount) {
                this.log(`未找到变量，请检查变量${ckNames.map(x => '[' + x + ']').join('或')}`, { notify: true })
                return false
            }
            this.log(`共找到${this.userCount}个账号`)
            return true
        }
        async UserThread(task, ...opt) {
            let taskAll = [];
            // 遍历所有用户
            for (let user of $.userList) {
                if (typeof task === 'string') {
                    // 情况 1：简单调用，task 是方法名
                    taskAll.push(user[task](...opt));
                } else {
                    // 情况 2：自定义逻辑，task 是函数
                    taskAll.push(task(user, ...opt));
                } 
            }
            // 等待所有任务完成，并返回结果
            return await Promise.all(taskAll);
        }
        async UserCycle(task, ...opt) {
            for (let user of $.userList) {
                if (typeof task === 'string'){
                    await user[task](...opt)
                }else{
                    // console.log(`\n\n====================  ${user.idx}  ====================`)
                    await task(user, ...opt)
                }                
            }
        } 
        async TaskThread(taskName, thread ,...opt) {
            let taskAll = []
            let bingfa = Math.abs(thread)
            while (bingfa--) {
                taskAll.push(taskName(...opt))
            }
            await Promise.all(taskAll)
        }
        async TaskCycle(taskName, thread ,...opt) {
            let rang = Math.abs(thread)
            let idx = 0 
            while (rang--) {
                idx++
                await taskName(...opt,idx)
            }
        } 
        time(t, x = null) {
            let xt = x ? new Date(x) : new Date
            let e = {
                "M+": xt.getMonth() + 1,
                "d+": xt.getDate(),
                "h+": xt.getHours(),
                "m+": xt.getMinutes(),
                "s+": xt.getSeconds(),
                "q+": Math.floor((xt.getMonth() + 3) / 3),
                S: this.padStr(xt.getMilliseconds(), 3)
            };
            /(y+)/.test(t) && (t = t.replace(RegExp.$1, (xt.getFullYear() + "").substr(4 - RegExp.$1.length)))
            for (let s in e)
                new RegExp("(" + s + ")").test(t) && (t = t.replace(RegExp.$1, 1 == RegExp.$1.length ? e[s] : ("00" + e[s]).substr(("" + e[s]).length)))
            return t
        }
        async showmsg() {
            if (!this.notifyFlag) return
            if (this.notifyStr.length==0) return
            //if (!this.notifyStr) return
            let notify = require('./sendNotify')
            this.log('\n============== 推送 ==============')
            await notify.sendNotify(this.name, this.notifyStr.join('\n'))
        }
        padStr(num, length, opt = {}) {
            let padding = opt.padding || '0'
            let mode = opt.mode || 'l'
            let numStr = String(num)
            let numPad = (length > numStr.length) ? (length - numStr.length) : 0
            let pads = ''
            for (let i = 0; i < numPad; i++) {
                pads += padding
            }
            if (mode == 'r') {
                numStr = numStr + pads
            } else {
                numStr = pads + numStr
            }
            return numStr
        }
        json2str(obj, c, encode = false) {
            let ret = []
            for (let keys of Object.keys(obj).sort()) {
                let v = obj[keys]
                if (v && encode) v = encodeURIComponent(v)
                ret.push(keys + '=' + v)
            }
            return ret.join(c)
        }
        str2json(str, decode = false) {
            let ret = {}
            for (let item of str.split('&')) {
                if (!item) continue
                let idx = item.indexOf('=')
                if (idx == -1) continue
                let k = item.substr(0, idx)
                let v = item.substr(idx + 1)
                if (decode) v = decodeURIComponent(v)
                ret[k] = v
            }
            return ret
        }
        phoneNum(phone_num) {
            if (phone_num.length == 11) {
                let data = phone_num.replace(/(\d{3})\d{4}(\d{4})/, "$1****$2")
                return data
            } else {
                return phone_num
            }
        }
        randomInt(min, max) {
            return Math.round(Math.random() * (max - min) + min)
        }
        async yiyan() {
            const got = require('got')
            return new Promise((resolve) => {
                (async () => {
                    try {
                        const response = await got('https://v1.hitokoto.cn')
                        // console.log(response.body)
                        let data = JSON.parse(response.body)
                        let data_ = `[一言]: ${data.hitokoto}  by--${data.from}`
                        // console.log(data_)
                        resolve(data_)
                    } catch (error) {
                        console.log(error.response.body)
                    }
                })()
            })
        }
        ts(type = false, _data = "") {
            let myDate = new Date()
            let a = ""
            switch (type) {
                case 10:
                    a = Math.round(new Date().getTime() / 1000).toString()
                    break
                case 13:
                    a = Math.round(new Date().getTime()).toString()
                    break
                case "h":
                    a = myDate.getHours()
                    break
                case "m":
                    a = myDate.getMinutes()
                    break
                case "y":
                    a = myDate.getFullYear()
                    break
                case "h":
                    a = myDate.getHours()
                    break
                case "mo":
                    a = myDate.getMonth()
                    break
                case "d":
                    a = myDate.getDate()
                    break
                case "ts2Data":
                    if (_data != "") {
                        time = _data
                        if (time.toString().length == 13) {
                            let date = new Date(time + 8 * 3600 * 1000)
                            a = date.toJSON().substr(0, 19).replace("T", " ")
                        } else if (time.toString().length == 10) {
                            time = time * 1000
                            let date = new Date(time + 8 * 3600 * 1000)
                            a = date.toJSON().substr(0, 19).replace("T", " ")
                        }
                    }
                    break
                default:
                    a = "未知错误,请检查"
                    break
            }
            return a
        }
        randomPattern(pattern, charset = 'abcdef0123456789') {
            let str = ''
            for (let chars of pattern) {
                if (chars == 'x') {
                    str += charset.charAt(Math.floor(Math.random() * charset.length))
                } else if (chars == 'X') {
                    str += charset.charAt(Math.floor(Math.random() * charset.length)).toUpperCase()
                } else {
                    str += chars
                }
            }
            return str
        }
        randomString(len, charset = 'abcdef0123456789') {
            let str = ''
            for (let i = 0; i < len; i++) {
                str += charset.charAt(Math.floor(Math.random() * charset.length))
            }
            return str
        }
        randomList(a) {
            let idx = Math.floor(Math.random() * a.length)
            return a[idx]
        }
        wait(t) {
            return new Promise(e => setTimeout(e, t * 1000))
        }
        async exitNow() {
            await this.showmsg()
            let e = Date.now()
            let s = (e - this.startTime) / 1000
            this.log(`\n\n[${this.name}]运行结束，共运行了${s}秒`)
            process.exit(0)
        }
    }(name)
}

//==========================MD5算法代码=====================================
function MD5(sMessage) { 
function RotateLeft(lValue, iShiftBits) { return (lValue<<iShiftBits) | (lValue>>>(32-iShiftBits)); } 
function AddUnsigned(lX,lY) { 
var lX4,lY4,lX8,lY8,lResult; 
lX8 = (lX & 0x80000000); 
lY8 = (lY & 0x80000000); 
lX4 = (lX & 0x40000000); 
lY4 = (lY & 0x40000000); 
lResult = (lX & 0x3FFFFFFF)+(lY & 0x3FFFFFFF); 
if (lX4 & lY4) return (lResult ^ 0x80000000 ^ lX8 ^ lY8); 
if (lX4 | lY4) { 
if (lResult & 0x40000000) return (lResult ^ 0xC0000000 ^ lX8 ^ lY8); 
else return (lResult ^ 0x40000000 ^ lX8 ^ lY8); 
} else return (lResult ^ lX8 ^ lY8); 
} 
function F(x,y,z) { return (x & y) | ((~x) & z); } 
function G(x,y,z) { return (x & z) | (y & (~z)); } 
function H(x,y,z) { return (x ^ y ^ z); } 
function I(x,y,z) { return (y ^ (x | (~z))); } 
function FF(a,b,c,d,x,s,ac) { 
a = AddUnsigned(a, AddUnsigned(AddUnsigned(F(b, c, d), x), ac)); 
return AddUnsigned(RotateLeft(a, s), b); 
} 
function GG(a,b,c,d,x,s,ac) { 
a = AddUnsigned(a, AddUnsigned(AddUnsigned(G(b, c, d), x), ac)); 
return AddUnsigned(RotateLeft(a, s), b); 
} 
function HH(a,b,c,d,x,s,ac) { 
a = AddUnsigned(a, AddUnsigned(AddUnsigned(H(b, c, d), x), ac)); 
return AddUnsigned(RotateLeft(a, s), b); 
} 
function II(a,b,c,d,x,s,ac) { 
a = AddUnsigned(a, AddUnsigned(AddUnsigned(I(b, c, d), x), ac)); 
return AddUnsigned(RotateLeft(a, s), b); 
} 
function ConvertToWordArray(sMessage) { 
var lWordCount; 
var lMessageLength = sMessage.length; 
var lNumberOfWords_temp1=lMessageLength + 8; 
var lNumberOfWords_temp2=(lNumberOfWords_temp1-(lNumberOfWords_temp1 % 64))/64; 
var lNumberOfWords = (lNumberOfWords_temp2+1)*16; 
var lWordArray=Array(lNumberOfWords-1); 
var lBytePosition = 0; 
var lByteCount = 0; 
while ( lByteCount < lMessageLength ) { 
lWordCount = (lByteCount-(lByteCount % 4))/4; 
lBytePosition = (lByteCount % 4)*8; 
lWordArray[lWordCount] = (lWordArray[lWordCount] | (sMessage.charCodeAt(lByteCount)<<lBytePosition)); 
lByteCount++; 
} 
lWordCount = (lByteCount-(lByteCount % 4))/4; 
lBytePosition = (lByteCount % 4)*8; 
lWordArray[lWordCount] = lWordArray[lWordCount] | (0x80<<lBytePosition); 
lWordArray[lNumberOfWords-2] = lMessageLength<<3; 
lWordArray[lNumberOfWords-1] = lMessageLength>>>29; 
return lWordArray; 
} 
function WordToHex(lValue) { 
var WordToHexValue="",WordToHexValue_temp="",lByte,lCount; 
for (lCount = 0;lCount<=3;lCount++) { 
lByte = (lValue>>>(lCount*8)) & 255; 
WordToHexValue_temp = "0" + lByte.toString(16); 
WordToHexValue = WordToHexValue + WordToHexValue_temp.substr(WordToHexValue_temp.length-2,2); 
} 
return WordToHexValue; 
} 
var x=Array(); 
var k,AA,BB,CC,DD,a,b,c,d 
var S11=7, S12=12, S13=17, S14=22; 
var S21=5, S22=9 , S23=14, S24=20; 
var S31=4, S32=11, S33=16, S34=23; 
var S41=6, S42=10, S43=15, S44=21; 
// Steps 1 and 2. Append padding bits and length and convert to words 
x = ConvertToWordArray(sMessage); 
// Step 3. Initialise 
a = 0x67452301; b = 0xEFCDAB89; c = 0x98BADCFE; d = 0x10325476; 
// Step 4. Process the message in 16-word blocks 
for (k=0;k<x.length;k+=16) { 
AA=a; BB=b; CC=c; DD=d; 
a=FF(a,b,c,d,x[k+0], S11,0xD76AA478); 
d=FF(d,a,b,c,x[k+1], S12,0xE8C7B756); 
c=FF(c,d,a,b,x[k+2], S13,0x242070DB); 
b=FF(b,c,d,a,x[k+3], S14,0xC1BDCEEE); 
a=FF(a,b,c,d,x[k+4], S11,0xF57C0FAF); 
d=FF(d,a,b,c,x[k+5], S12,0x4787C62A); 
c=FF(c,d,a,b,x[k+6], S13,0xA8304613); 
b=FF(b,c,d,a,x[k+7], S14,0xFD469501); 
a=FF(a,b,c,d,x[k+8], S11,0x698098D8); 
d=FF(d,a,b,c,x[k+9], S12,0x8B44F7AF); 
c=FF(c,d,a,b,x[k+10],S13,0xFFFF5BB1); 
b=FF(b,c,d,a,x[k+11],S14,0x895CD7BE); 
a=FF(a,b,c,d,x[k+12],S11,0x6B901122); 
d=FF(d,a,b,c,x[k+13],S12,0xFD987193); 
c=FF(c,d,a,b,x[k+14],S13,0xA679438E); 
b=FF(b,c,d,a,x[k+15],S14,0x49B40821); 
a=GG(a,b,c,d,x[k+1], S21,0xF61E2562); 
d=GG(d,a,b,c,x[k+6], S22,0xC040B340); 
c=GG(c,d,a,b,x[k+11],S23,0x265E5A51); 
b=GG(b,c,d,a,x[k+0], S24,0xE9B6C7AA); 
a=GG(a,b,c,d,x[k+5], S21,0xD62F105D); 
d=GG(d,a,b,c,x[k+10],S22,0x2441453); 
c=GG(c,d,a,b,x[k+15],S23,0xD8A1E681); 
b=GG(b,c,d,a,x[k+4], S24,0xE7D3FBC8); 
a=GG(a,b,c,d,x[k+9], S21,0x21E1CDE6); 
d=GG(d,a,b,c,x[k+14],S22,0xC33707D6); 
c=GG(c,d,a,b,x[k+3], S23,0xF4D50D87); 
b=GG(b,c,d,a,x[k+8], S24,0x455A14ED); 
a=GG(a,b,c,d,x[k+13],S21,0xA9E3E905); 
d=GG(d,a,b,c,x[k+2], S22,0xFCEFA3F8); 
c=GG(c,d,a,b,x[k+7], S23,0x676F02D9); 
b=GG(b,c,d,a,x[k+12],S24,0x8D2A4C8A); 
a=HH(a,b,c,d,x[k+5], S31,0xFFFA3942); 
d=HH(d,a,b,c,x[k+8], S32,0x8771F681); 
c=HH(c,d,a,b,x[k+11],S33,0x6D9D6122); 
b=HH(b,c,d,a,x[k+14],S34,0xFDE5380C); 
a=HH(a,b,c,d,x[k+1], S31,0xA4BEEA44); 
d=HH(d,a,b,c,x[k+4], S32,0x4BDECFA9); 
c=HH(c,d,a,b,x[k+7], S33,0xF6BB4B60); 
b=HH(b,c,d,a,x[k+10],S34,0xBEBFBC70); 
a=HH(a,b,c,d,x[k+13],S31,0x289B7EC6); 
d=HH(d,a,b,c,x[k+0], S32,0xEAA127FA); 
c=HH(c,d,a,b,x[k+3], S33,0xD4EF3085); 
b=HH(b,c,d,a,x[k+6], S34,0x4881D05); 
a=HH(a,b,c,d,x[k+9], S31,0xD9D4D039); 
d=HH(d,a,b,c,x[k+12],S32,0xE6DB99E5); 
c=HH(c,d,a,b,x[k+15],S33,0x1FA27CF8); 
b=HH(b,c,d,a,x[k+2], S34,0xC4AC5665); 
a=II(a,b,c,d,x[k+0], S41,0xF4292244); 
d=II(d,a,b,c,x[k+7], S42,0x432AFF97); 
c=II(c,d,a,b,x[k+14],S43,0xAB9423A7); 
b=II(b,c,d,a,x[k+5], S44,0xFC93A039); 
a=II(a,b,c,d,x[k+12],S41,0x655B59C3); 
d=II(d,a,b,c,x[k+3], S42,0x8F0CCC92); 
c=II(c,d,a,b,x[k+10],S43,0xFFEFF47D); 
b=II(b,c,d,a,x[k+1], S44,0x85845DD1); 
a=II(a,b,c,d,x[k+8], S41,0x6FA87E4F); 
d=II(d,a,b,c,x[k+15],S42,0xFE2CE6E0); 
c=II(c,d,a,b,x[k+6], S43,0xA3014314); 
b=II(b,c,d,a,x[k+13],S44,0x4E0811A1); 
a=II(a,b,c,d,x[k+4], S41,0xF7537E82); 
d=II(d,a,b,c,x[k+11],S42,0xBD3AF235); 
c=II(c,d,a,b,x[k+2], S43,0x2AD7D2BB); 
b=II(b,c,d,a,x[k+9], S44,0xEB86D391); 
a=AddUnsigned(a,AA); b=AddUnsigned(b,BB); c=AddUnsigned(c,CC); d=AddUnsigned(d,DD); 
} 
var TypNN;

if(true){TypNN = WordToHex(a)+WordToHex(b)+WordToHex(c)+WordToHex(d);}
var temp= TypNN; 
return temp;
}

// 当前脚本来自于 http://script.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cn 脚本库下载！
// 当前脚本来自于 http://2.345yun.cc 脚本库下载！
// 脚本库官方QQ群1群: 429274456
// 脚本库官方QQ群2群: 1077801222
// 脚本库官方QQ群3群: 433030897
// 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
// 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
// 您在使用脚本库下载的脚本时自行检查判断风险。
// 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。