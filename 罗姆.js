/*
微信小程序:罗姆积分商城
抓取的域名 rohmpointmall.geomatrixpr.com
随便查看一条请求头里的user_id=XXXXX 只需要数字
变量
luomu='12345'抓取的user_id
多账户@隔开
corn 0 1 * * *
*/
const $ = new Env('罗姆');

let status;
status = (status = ($.getval("luomustatus") || "1") ) > 1 ? `${status}` : ""; // 账号扩展字符
let luomuArr = [],luomucount = ''

let luomu= $.isNode() ? (process.env.luomu ? process.env.luomu : "") : ($.getdata('luomu') ? $.getdata('luomu') : "")
let luomus = ""
const logs =0;
const host='https://rohmpointmall.geomatrixpr.com/backend/public/index.php/api/'
var hours = new Date().getHours();
var ssss = new Date().getMinutes();

var timestamp = Math.round(new Date().getTime()/1000).toString();
!(async () => {
  if (typeof $request !== "undefined") {
        await luomuck()
  } else {
      if(!$.isNode()){
          luomuArr.push($.getdata('luomu'))
          let luomucount = ($.getval('luomucount') || '1');
          for (let i = 2; i <= luomucount; i++) {
            luomuArr.push($.getdata(`luomu${i}`))
            }
    console.log(`------------- 共${luomuArr.length}个账号-------------\n`)
      for (let i = 0; i < luomuArr.length; i++) {
        if (luomuArr[i]) {
          luomu = luomuArr[i];
          $.index = i + 1;
await main()
  }
}
      }else  {
          if (process.env.luomu && process.env.luomu.indexOf('@') > -1) {
            luomuArr = process.env.luomu.split('@');
            console.log(`您选择的是用"@"隔开\n`)
        } else {
            luomus = [process.env.luomu]
        };
        Object.keys(luomus).forEach((item) => {
        if (luomus[item]) {
            luomuArr.push(luomus[item])
        }
    })
          console.log(`共${luomuArr.length}个账号`)
          console.log(`${luomu}\n`)
	        for (let k = 0; k < luomuArr.length; k++) {
                $.message = ""
                luomu = luomuArr[k]
                $.index = k + 1;
await main()
}

      }
  }
})()
  .catch((e) => $.logErr(e))
  .finally(() => $.done())

async function main(){
    $.log('签到')
await signin()

$.log('浏览新闻')
await log_pv('https%3A%2F%2Fwww.rohm.com.cn%2Fnews-detail%3Fnews-title%3D2022-07-26_news_ldo%26defaultGroupId%3Dfalse%26utm_medium%3Dsocial%26utm_source%3Dwechat%26utm_campaign%3DWeChat(infor)%26utm_content%3DPointsMall&title=ROHM%E5%BC%80%E5%8F%91%E5%87%BA%E4%BD%BF%E7%94%A8%E7%BA%B3%E6%B3%95%E7%BA%A7%E8%B6%85%E5%B0%8F%E7%94%B5%E5%AE%B9%E4%B9%9F%E8%83%BD%E7%A8%B3%E5%AE%9A%E8%BF%90%E8%A1%8C%E7%9A%84%E5%86%85%E7%BD%AE%E6%96%B0%E7%94%B5%E8%B7%AF%E7%9A%84%E8%BD%A6%E8%BD%BDLDO%E7%A8%B3%E5%8E%8B%E5%99%A8%E2%80%9CBD9xxN1%E7%B3%BB%E5%88%97%E2%80%9D',4)
await $.wait(10000)
await read_log('https%3A%2F%2Fwww.rohm.com.cn%2Fnews-detail%3Fnews-title%3D2022-07-26_news_ldo%26defaultGroupId%3Dfalse%26utm_medium%3Dsocial%26utm_source%3Dwechat%26utm_campaign%3DWeChat(infor)%26utm_content%3DPointsMall&title=ROHM%E5%BC%80%E5%8F%91%E5%87%BA%E4%BD%BF%E7%94%A8%E7%BA%B3%E6%B3%95%E7%BA%A7%E8%B6%85%E5%B0%8F%E7%94%B5%E5%AE%B9%E4%B9%9F%E8%83%BD%E7%A8%B3%E5%AE%9A%E8%BF%90%E8%A1%8C%E7%9A%84%E5%86%85%E7%BD%AE%E6%96%B0%E7%94%B5%E8%B7%AF%E7%9A%84%E8%BD%A6%E8%BD%BDLDO%E7%A8%B3%E5%8E%8B%E5%99%A8%E2%80%9CBD9xxN1%E7%B3%BB%E5%88%97%E2%80%9D',4)
await log_pv('https%3A%2F%2Fwww.rohm.com.cn%2Fnews-detail%3Fnews-title%3D2022-07-21_news_serdes%26defaultGroupId%3Dfalse%26utm_medium%3Dsocial%26utm_source%3Dwechat%26utm_campaign%3DWeChat(infor)%26utm_content%3DPointsMall&title=ROHM%E5%BC%80%E5%8F%91%E5%87%BA%E5%8F%AF%E7%AE%80%E5%8C%96%E8%A7%86%E9%A2%91%E4%BC%A0%E8%BE%93%E8%B7%AF%E5%BE%84%E7%9A%84%E3%80%81%3Cbr%3E%E7%94%A8%E4%BA%8E%E8%BD%A6%E8%BD%BD%E5%A4%9A%E5%B1%8F%E6%98%BE%E7%A4%BA%E5%99%A8%E7%9A%84%E4%B8%B2%E8%A1%8C%2F%E8%A7%A3%E4%B8%B2%E5%99%A8%E2%80%9CBU18xx82-M%E2%80%9D',4)
await $.wait(10000)
await read_log('https%3A%2F%2Fwww.rohm.com.cn%2Fnews-detail%3Fnews-title%3D2022-07-21_news_serdes%26defaultGroupId%3Dfalse%26utm_medium%3Dsocial%26utm_source%3Dwechat%26utm_campaign%3DWeChat(infor)%26utm_content%3DPointsMall&title=ROHM%E5%BC%80%E5%8F%91%E5%87%BA%E5%8F%AF%E7%AE%80%E5%8C%96%E8%A7%86%E9%A2%91%E4%BC%A0%E8%BE%93%E8%B7%AF%E5%BE%84%E7%9A%84%E3%80%81%3Cbr%3E%E7%94%A8%E4%BA%8E%E8%BD%A6%E8%BD%BD%E5%A4%9A%E5%B1%8F%E6%98%BE%E7%A4%BA%E5%99%A8%E7%9A%84%E4%B8%B2%E8%A1%8C%2F%E8%A7%A3%E4%B8%B2%E5%99%A8%E2%80%9CBU18xx82-M%E2%80%9D',4)

$.log('浏览博客')
await log_pv('https%3A%2F%2Fwww.rohm.com.cn%2Fblog%2FElectronicsforthefuture&title=%E7%94%A8%E7%94%B5%E5%AD%90%E5%85%83%E5%99%A8%E4%BB%B6%E8%A7%A3%E5%86%B3%E7%A4%BE%E4%BC%9A%E9%97%AE%E9%A2%98%EF%BC%8C%E4%B8%BA%E6%96%87%E5%8C%96%E7%9A%84%E8%BF%9B%E6%AD%A5%E4%B8%8E%E6%8F%90%E9%AB%98%E5%81%9A%E5%87%BA%E8%B4%A1%E7%8C%AE',5)
await $.wait(10000)
await read_log('https%3A%2F%2Fwww.rohm.com.cn%2Fblog%2FElectronicsforthefuture&title=%E7%94%A8%E7%94%B5%E5%AD%90%E5%85%83%E5%99%A8%E4%BB%B6%E8%A7%A3%E5%86%B3%E7%A4%BE%E4%BC%9A%E9%97%AE%E9%A2%98%EF%BC%8C%E4%B8%BA%E6%96%87%E5%8C%96%E7%9A%84%E8%BF%9B%E6%AD%A5%E4%B8%8E%E6%8F%90%E9%AB%98%E5%81%9A%E5%87%BA%E8%B4%A1%E7%8C%AE',5)

$.log('微信文章')
await log_pv('https%3A%2F%2Fmp.weixin.qq.com%2Fs%2Fo65aGqltTHFrxSxAd7vMDg&title=%E4%BB%8A%E6%97%A5%E4%B8%8A%E5%8D%88%E5%8D%81%E7%82%B9%EF%BC%81%E7%BD%97%E5%A7%86%E7%A0%94%E8%AE%A8%E4%BC%9A%E5%BC%80%E6%92%AD~',6)
await $.wait(10000)
await read_log('https%3A%2F%2Fmp.weixin.qq.com%2Fs%2Fo65aGqltTHFrxSxAd7vMDg&title=%E4%BB%8A%E6%97%A5%E4%B8%8A%E5%8D%88%E5%8D%81%E7%82%B9%EF%BC%81%E7%BD%97%E5%A7%86%E7%A0%94%E8%AE%A8%E4%BC%9A%E5%BC%80%E6%92%AD~',6)
await log_pv('https%3A%2F%2Fmp.weixin.qq.com%2Fs%2FYIsOMNwNv8uN-7Q1dwKLww&title=%E6%B5%8B%E8%AF%84%20%7C%20BM1Z102FJ-EVK-001%E8%BF%87%E9%9B%B6%E6%A3%80%E6%B5%8BEVK%E8%AF%84%E4%BC%B0%E6%9D%BF%E8%A7%A3%E5%AF%86%EF%BC%885%EF%BC%89',6)
await $.wait(10000)
await read_log('https%3A%2F%2Fmp.weixin.qq.com%2Fs%2FYIsOMNwNv8uN-7Q1dwKLww&title=%E6%B5%8B%E8%AF%84%20%7C%20BM1Z102FJ-EVK-001%E8%BF%87%E9%9B%B6%E6%A3%80%E6%B5%8BEVK%E8%AF%84%E4%BC%B0%E6%9D%BF%E8%A7%A3%E5%AF%86%EF%BC%885%EF%BC%89',6)

$.log('电子小知识')
await log_pv('https%3A%2F%2Fwww.rohm.com.cn%2Felectronics-basics%2Ftransistors%2Ftr_what1%3Futm_medium%3Dsocial%26utm_source%3Dwesite%26utm_campaign%3DCN_(wesite)_Electronics%2520Basics%26utm_medium%3Dsocial%26utm_source%3Dwechat%26utm_campaign%3DWeChat(infor)%26utm_content%3DPointsMall&title=undefined',9)
await $.wait(10000)
await read_log('https%3A%2F%2Fwww.rohm.com.cn%2Felectronics-basics%2Ftransistors%2Ftr_what1%3Futm_medium%3Dsocial%26utm_source%3Dwesite%26utm_campaign%3DCN_(wesite)_Electronics%2520Basics%26utm_medium%3Dsocial%26utm_source%3Dwechat%26utm_campaign%3DWeChat(infor)%26utm_content%3DPointsMall&title=undefined',9)
await log_pv('https://www.rohm.com.cn/electronics-basics/transistors/tr_what2?utm_medium=social&utm_source=wesite&utm_campaign=CN_(wesite)_Electronics%20Basics&utm_medium=social&utm_source=wechat&utm_campaign=WeChat(infor)&utm_content=PointsMall&title=undefined',9)
await $.wait(10000)
await read_log('https://www.rohm.com.cn/electronics-basics/transistors/tr_what2?utm_medium=social&utm_source=wesite&utm_campaign=CN_(wesite)_Electronics%20Basics&utm_medium=social&utm_source=wechat&utm_campaign=WeChat(infor)&utm_content=PointsMall&title=undefined',9)

$.log('技术文章')
await log_pv('https%3A%2F%2Ftechclass.rohm.com.cn%2Fknowledge%2Ftech-info%2Farduino%2Farduino-chicken-racer&title=undefined',8)
await $.wait(10000)
await read_log('https%3A%2F%2Ftechclass.rohm.com.cn%2Fknowledge%2Ftech-info%2Farduino%2Farduino-chicken-racer&title=undefined',8)

$.log('观看视频')
await log_pv('https%3A%2F%2Frohmweixin.geomatrixpr.com%2Frohm%2Fvideo%2Fdetail%2F47&title=%E7%AC%AC4%E4%BB%A3650V%E5%BF%AB%E9%80%9F%E6%81%A2%E5%A4%8D%E4%BA%8C%E6%9E%81%E7%AE%A1',7)
await $.wait(30000)
await read_log('https%3A%2F%2Frohmweixin.geomatrixpr.com%2Frohm%2Fvideo%2Fdetail%2F47&title=%E7%AC%AC4%E4%BB%A3650V%E5%BF%AB%E9%80%9F%E6%81%A2%E5%A4%8D%E4%BA%8C%E6%9E%81%E7%AE%A1',7)
}
function luomuck() {
   if ($request.url.indexOf("my_task") > -1) {
  const luomu1 = $request.body

if(luomu)    $.setdata(luomu,`luomu${status}`)


luomu=luomu1.match(/'user_id=(.*?)'/)
$.msg(luomu)

}
}
function signin() {
 return new Promise((resolve) => {
  
$.post(lmpost(`Api/user_signin`,'user_id='+luomu), async (err, resp, data) => {
      
      try {
        if (err) {
          console.log(`${JSON.stringify(err)}`)
          console.log(`${$.name} API请求失败，请检查网路重试`)
        }// else {
          if (safeGet(data)) {
            data = JSON.parse(data);
             if(data.code==1){

               console.log(data.msg)  
}
             else if(data.code == 102){
             console.log(data.msg)
             
             }
          }
        
      } catch (e) {
        $.logErr(e, resp)
      } finally {
        resolve(data);
      }
    })
  })
}

function log_pv(a,task_id) {
 return new Promise((resolve) => {
  
$.post(lmpost(`pv/log_pv`,'url='+a+'&user_id='+luomu+'&task_id='+task_id), async (err, resp, data) => {
       
      try {
        if (err) {
          console.log(`${JSON.stringify(err)}`)
          console.log(`${$.name} API请求失败，请检查网路重试`)
        }// else {
          if (safeGet(data)) {
            data = JSON.parse(data);
             if(data.code==1){

               console.log(data.msg)  
}
             else if(data.code == 0){
             console.log(data.msg)
             
             }
          }
        
      } catch (e) {
        $.logErr(e, resp)
      } finally {
        resolve(data);
      }
    })
  })
}
function read_log(a,task_id) {
 return new Promise((resolve) => {
  
$.post(lmpost(`Api/read_log`,'user_id='+luomu+'&pointstask_id='+task_id+'&url='+a), async (err, resp, data) => {
      
      try {
        if (err) {
          console.log(`${JSON.stringify(err)}`)
          console.log(`${$.name} API请求失败，请检查网路重试`)
        }// else {
          if (safeGet(data)) {
            data = JSON.parse(data);
             if(data.code==2){

               console.log(data.msg)  
}
             else if(data.code == 0){
             console.log(data.msg)
             
             }
          }
        
      } catch (e) {
        $.logErr(e, resp)
      } finally {
        resolve(data);
      }
    })
  })
}
function lmget(a) {
  return {

    url: `${host1}${a}`,
    headers: {
'Host': 'rohmpointmall.geomatrixpr.com',
'Connection': 'keep-alive',
'xweb_xhr': '1',
'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 MicroMessenger/7.0.4.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF',
'Content-Type': 'application/x-www-form-urlencoded',
'Referer': 'https://servicewechat.com/wxba8fadd97f0c6847/42/page-frame.html',
'Accept-Language': 'en-us,en',
'Accept-Encoding': 'gzip, deflate',
    }
  }
}
function lmpost(a,b) {
  return {

    url: `${host}${a}`,
    body:`${b}`,
    headers: {
'Host': 'rohmpointmall.geomatrixpr.com',
'Connection': 'keep-alive',
'xweb_xhr': '1',
'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 MicroMessenger/7.0.4.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF',
'Content-Type': 'application/x-www-form-urlencoded',
'Referer': 'https://servicewechat.com/wxba8fadd97f0c6847/42/page-frame.html',
'Accept-Language': 'en-us,en',
'Accept-Encoding': 'gzip, deflate',

    }
  }
}
function safeGet(data) {
  try {
    if (typeof JSON.parse(data) == "object") {
      return true;
    }
  } catch (e) {
    console.log(e);
    console.log(`服务器访问数据为空，请检查自身设备网络情况`);
    return false;
  }
}
function jsonParse(str) {
  if (typeof str == "string") {
    try {
      return JSON.parse(str);
    } catch (e) {
      console.log(e);
      $.msg($.name, '', '请勿随意在BoxJs输入框修改内容\n建议通过脚本去获取cookie')
      return [];
    }
  }
}
function Env(t,e){class s{constructor(t){this.env=t}send(t,e="GET"){t="string"==typeof t?{url:t}:t;let s=this.get;return"POST"===e&&(s=this.post),new Promise((e,i)=>{s.call(this,t,(t,s,r)=>{t?i(t):e(s)})})}get(t){return this.send.call(this.env,t)}post(t){return this.send.call(this.env,t,"POST")}}return new class{constructor(t,e){this.name=t,this.http=new s(this),this.data=null,this.dataFile="box.dat",this.logs=[],this.isMute=!1,this.isNeedRewrite=!1,this.logSeparator="\n",this.startTime=(new Date).getTime(),Object.assign(this,e),this.log("",`\ud83d\udd14${this.name}, \u5f00\u59cb!`)}isNode(){return"undefined"!=typeof module&&!!module.exports}isQuanX(){return"undefined"!=typeof $task}isSurge(){return"undefined"!=typeof $httpClient&&"undefined"==typeof $loon}isLoon(){return"undefined"!=typeof $loon}toObj(t,e=null){try{return JSON.parse(t)}catch{return e}}toStr(t,e=null){try{return JSON.stringify(t)}catch{return e}}getjson(t,e){let s=e;const i=this.getdata(t);if(i)try{s=JSON.parse(this.getdata(t))}catch{}return s}setjson(t,e){try{return this.setdata(JSON.stringify(t),e)}catch{return!1}}getScript(t){return new Promise(e=>{this.get({url:t},(t,s,i)=>e(i))})}runScript(t,e){return new Promise(s=>{let i=this.getdata("@chavy_boxjs_userCfgs.httpapi");i=i?i.replace(/\n/g,"").trim():i;let r=this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout");r=r?1*r:20,r=e&&e.timeout?e.timeout:r;const[o,h]=i.split("@"),a={url:`http://${h}/v1/scripting/evaluate`,body:{script_text:t,mock_type:"cron",timeout:r},headers:{"X-Key":o,Accept:"*/*"}};this.post(a,(t,e,i)=>s(i))}).catch(t=>this.logErr(t))}loaddata(){if(!this.isNode())return{};{this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e);if(!s&&!i)return{};{const i=s?t:e;try{return JSON.parse(this.fs.readFileSync(i))}catch(t){return{}}}}}writedata(){if(this.isNode()){this.fs=this.fs?this.fs:require("fs"),this.path=this.path?this.path:require("path");const t=this.path.resolve(this.dataFile),e=this.path.resolve(process.cwd(),this.dataFile),s=this.fs.existsSync(t),i=!s&&this.fs.existsSync(e),r=JSON.stringify(this.data);s?this.fs.writeFileSync(t,r):i?this.fs.writeFileSync(e,r):this.fs.writeFileSync(t,r)}}lodash_get(t,e,s){const i=e.replace(/\[(\d+)\]/g,".$1").split(".");let r=t;for(const t of i)if(r=Object(r)[t],void 0===r)return s;return r}lodash_set(t,e,s){return Object(t)!==t?t:(Array.isArray(e)||(e=e.toString().match(/[^.[\]]+/g)||[]),e.slice(0,-1).reduce((t,s,i)=>Object(t[s])===t[s]?t[s]:t[s]=Math.abs(e[i+1])>>0==+e[i+1]?[]:{},t)[e[e.length-1]]=s,t)}getdata(t){let e=this.getval(t);if(/^@/.test(t)){const[,s,i]=/^@(.*?)\.(.*?)$/.exec(t),r=s?this.getval(s):"";if(r)try{const t=JSON.parse(r);e=t?this.lodash_get(t,i,""):e}catch(t){e=""}}return e}setdata(t,e){let s=!1;if(/^@/.test(e)){const[,i,r]=/^@(.*?)\.(.*?)$/.exec(e),o=this.getval(i),h=i?"null"===o?null:o||"{}":"{}";try{const e=JSON.parse(h);this.lodash_set(e,r,t),s=this.setval(JSON.stringify(e),i)}catch(e){const o={};this.lodash_set(o,r,t),s=this.setval(JSON.stringify(o),i)}}else s=this.setval(t,e);return s}getval(t){return this.isSurge()||this.isLoon()?$persistentStore.read(t):this.isQuanX()?$prefs.valueForKey(t):this.isNode()?(this.data=this.loaddata(),this.data[t]):this.data&&this.data[t]||null}setval(t,e){return this.isSurge()||this.isLoon()?$persistentStore.write(t,e):this.isQuanX()?$prefs.setValueForKey(t,e):this.isNode()?(this.data=this.loaddata(),this.data[e]=t,this.writedata(),!0):this.data&&this.data[e]||null}initGotEnv(t){this.got=this.got?this.got:require("got"),this.cktough=this.cktough?this.cktough:require("tough-cookie"),this.ckjar=this.ckjar?this.ckjar:new this.cktough.CookieJar,t&&(t.headers=t.headers?t.headers:{},void 0===t.headers.Cookie&&void 0===t.cookieJar&&(t.cookieJar=this.ckjar))}get(t,e=(()=>{})){t.headers&&(delete t.headers["Content-Type"],delete t.headers["Content-Length"]),this.isSurge()||this.isLoon()?(this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient.get(t,(t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status),e(t,s,i)})):this.isQuanX()?(this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>e(t))):this.isNode()&&(this.initGotEnv(t),this.got(t).on("redirect",(t,e)=>{try{if(t.headers["set-cookie"]){const s=t.headers["set-cookie"].map(this.cktough.Cookie.parse).toString();s&&this.ckjar.setCookieSync(s,null),e.cookieJar=this.ckjar}}catch(t){this.logErr(t)}}).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>{const{message:s,response:i}=t;e(s,i,i&&i.body)}))}post(t,e=(()=>{})){if(t.body&&t.headers&&!t.headers["Content-Type"]&&(t.headers["Content-Type"]="application/x-www-form-urlencoded"),t.headers&&delete t.headers["Content-Length"],this.isSurge()||this.isLoon())this.isSurge()&&this.isNeedRewrite&&(t.headers=t.headers||{},Object.assign(t.headers,{"X-Surge-Skip-Scripting":!1})),$httpClient.post(t,(t,s,i)=>{!t&&s&&(s.body=i,s.statusCode=s.status),e(t,s,i)});else if(this.isQuanX())t.method="POST",this.isNeedRewrite&&(t.opts=t.opts||{},Object.assign(t.opts,{hints:!1})),$task.fetch(t).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>e(t));else if(this.isNode()){this.initGotEnv(t);const{url:s,...i}=t;this.got.post(s,i).then(t=>{const{statusCode:s,statusCode:i,headers:r,body:o}=t;e(null,{status:s,statusCode:i,headers:r,body:o},o)},t=>{const{message:s,response:i}=t;e(s,i,i&&i.body)})}}time(t){let e={"M+":(new Date).getMonth()+1,"d+":(new Date).getDate(),"H+":(new Date).getHours(),"m+":(new Date).getMinutes(),"s+":(new Date).getSeconds(),"q+":Math.floor(((new Date).getMonth()+3)/3),S:(new Date).getMilliseconds()};/(y+)/.test(t)&&(t=t.replace(RegExp.$1,((new Date).getFullYear()+"").substr(4-RegExp.$1.length)));for(let s in e)new RegExp("("+s+")").test(t)&&(t=t.replace(RegExp.$1,1==RegExp.$1.length?e[s]:("00"+e[s]).substr((""+e[s]).length)));return t}msg(e=t,s="",i="",r){const o=t=>{if(!t)return t;if("string"==typeof t)return this.isLoon()?t:this.isQuanX()?{"open-url":t}:this.isSurge()?{url:t}:void 0;if("object"==typeof t){if(this.isLoon()){let e=t.openUrl||t.url||t["open-url"],s=t.mediaUrl||t["media-url"];return{openUrl:e,mediaUrl:s}}if(this.isQuanX()){let e=t["open-url"]||t.url||t.openUrl,s=t["media-url"]||t.mediaUrl;return{"open-url":e,"media-url":s}}if(this.isSurge()){let e=t.url||t.openUrl||t["open-url"];return{url:e}}}};if(this.isMute||(this.isSurge()||this.isLoon()?$notification.post(e,s,i,o(r)):this.isQuanX()&&$notify(e,s,i,o(r))),!this.isMuteLog){let t=["","==============\ud83d\udce3\u7cfb\u7edf\u901a\u77e5\ud83d\udce3=============="];t.push(e),s&&t.push(s),i&&t.push(i),console.log(t.join("\n")),this.logs=this.logs.concat(t)}}log(...t){t.length>0&&(this.logs=[...this.logs,...t]),console.log(t.join(this.logSeparator))}logErr(t,e){const s=!this.isSurge()&&!this.isQuanX()&&!this.isLoon();s?this.log("",`\u2757\ufe0f${this.name}, \u9519\u8bef!`,t.stack):this.log("",`\u2757\ufe0f${this.name}, \u9519\u8bef!`,t)}wait(t){return new Promise(e=>setTimeout(e,t))}done(t={}){const e=(new Date).getTime(),s=(e-this.startTime)/1e3;this.log("",`\ud83d\udd14${this.name}, \u7ed3\u675f! \ud83d\udd5b ${s} \u79d2`),this.log(),(this.isSurge()||this.isQuanX()||this.isLoon())&&$done(t)}}(t,e)}
