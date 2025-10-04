// 当前脚本来自于http://script.345yun.cn脚本库下载！
/*!
卡密变量名称: km
卡密变量值: https://t.me/+4ccNiabMEJkxZDVl
ck变量名称: ksck
格式:  ck#salt#代理
多号&分割
代理格式:  ip|端口|账号|密码
本脚本来自: http://2.345yun.cn 下载
 */

const request = require("request");
const querystring = require("querystring");
const { SocksProxyAgent } = require("socks-proxy-agent");

process.noDeprecation = true;

// 检测是否支持颜色输出
const supportsColor = process.stdout.isTTY && process.env.FORCE_COLOR !== '0';

// 简单的颜色函数
const colors = {
  red: (text) => supportsColor ? `\x1b[31m${text}\x1b[0m` : text,
  green: (text) => supportsColor ? `\x1b[32m${text}\x1b[0m` : text,
  yellow: (text) => supportsColor ? `\x1b[33m${text}\x1b[0m` : text,
  blue: (text) => supportsColor ? `\x1b[34m${text}\x1b[0m` : text,
  magenta: (text) => supportsColor ? `\x1b[35m${text}\x1b[0m` : text,
  cyan: (text) => supportsColor ? `\x1b[36m${text}\x1b[0m` : text,
  bold: (text) => supportsColor ? `\x1b[1m${text}\x1b[0m` : text
};

// 生成随机交互消息
function generateRandomInteractionMessage() {
  const messages = [
    "正在观看广告", 
    "认真观看中...", 
    "浏览广告内容", 
    "模拟用户行为", 
    "观看视频广告", 
    "保持活跃状态", 
    "广告浏览中", 
    "正常观看时长"
  ];
  return messages[Math.floor(Math.random() * messages.length)];
}

// 开发模式和环境变量检测
const isDevMode = process.env.DEV_MODE === "1" || process.env.DEV_MODE === "true";

// 账号颜色映射
const accountColors = [
  colors.blue,
  colors.green,
  colors.yellow,
  colors.magenta,
  colors.cyan,
  (text) => text, // 默认无颜色
  (text) => text, // 默认无颜色
  colors.blue,
  colors.green,
  colors.yellow,
  colors.magenta,
  colors.cyan
];

// 获取账号颜色
function getAccountColor(index) {
  return accountColors[(index - 1) % accountColors.length];
}

// 从单一ksck环境变量获取多个配置
function getAccountConfigsFromEnv() {
  const ksckValue = process.env.ksck;
  if (!ksckValue) {
    console.log("未找到 ksck 环境变量");
    return [];
  }
  
  const configStrings = ksckValue.split('&').map(config => config.trim()).filter(Boolean);
  console.log(`解析到 ${configStrings.length} 个配置`);
  
  return configStrings;
}

const accountConfigs = getAccountConfigsFromEnv();
const accountCount = accountConfigs.length;

console.log(colors.bold("快手国庆免费金币版启动！"));
console.log(colors.bold("青龙面板脚本库→http://2.345yun.cn"));

if (accountCount > (process.env.MAX_CONCURRENCY || 1000)) {
  console.log("错误: 检测到 " + accountCount + " 个账号配置，最多只允许" + (process.env.MAX_CONCURRENCY || 1000) + "个");
  process.exit(1);
}

// API配置
const baseRemoteUrl = "http://111.170.33.15:11678";
const proxyApiUrl = baseRemoteUrl + "/sign.php";
const queueStatusApiUrl = baseRemoteUrl + "/queue_status";

// 生成快手设备ID
function generateKuaishouDid() {
  try {
    const generateRandomHexString = (length) => {
      const hexChars = "0123456789abcdef";
      let result = "";
      for (let i = 0; i < length; i++) {
        result += hexChars.charAt(Math.floor(Math.random() * hexChars.length));
      }
      return result;
    };
    
    const randomId = generateRandomHexString(16);
    const deviceId = "ANDROID_" + randomId;
    return deviceId;
  } catch (error) {
    console.log("生成did失败: " + error.message);
    const timestamp = Date.now().toString(16).toUpperCase();
    return "ANDROID_" + timestamp.substring(0, 16);
  }
}

// 发送网络请求
async function sendRequest(requestOptions, proxyUrl = null, description = "Unknown Request") {
  const finalOptions = { ...requestOptions };
  
  if (proxyUrl) {
    try {
      finalOptions.agent = new SocksProxyAgent(proxyUrl);
    } catch (proxyError) {
      console.log(description + " 代理URL无效，尝试直连模式");
    }
  }
  
  return new Promise(resolve => {
    request(finalOptions, (error, response, body) => {
      if (error) {
        console.log(description + " 请求错误: " + (error.message || String(error)));
        return resolve(null);
      }
      
      if (!response || response.statusCode !== 200) {
        const statusCode = response ? response.statusCode : "无响应";
        console.log(description + " HTTP状态码异常: " + statusCode);
        return resolve(null);
      }
      
      try {
        resolve(JSON.parse(body));
      } catch {
        resolve(body);
      }
    });
  });
}

// 测试代理连通性
async function testProxyConnectivity(proxyUrl, description = "代理连通性检测") {
  if (!proxyUrl) {
    return {
      ok: true,
      msg: "未配置代理（直连模式）",
      ip: "localhost"
    };
  }
  
  const result = await sendRequest({
    method: "GET",
    url: "https://ipinfo.io/json",
    headers: {
      "User-Agent": "ProxyTester/1.0"
    },
    timeout: 8000
  }, proxyUrl, description);
  
  if (!result) {
    return {
      ok: false,
      msg: "无法通过代理访问 ipinfo.io",
      ip: ""
    };
  }
  
  const ip = result.ip || result.ip_address || "";
  return {
    ok: true,
    msg: "SOCKS5代理正常，出口IP: " + (ip || "未知"),
    ip: ip || "未知"
  };
}

const usedProxies = new Set();

// 获取账号基本信息
async function getAccountBasicInfo(cookie, proxyUrl, accountId = "?") {
  const url = "https://nebula.kuaishou.com/rest/n/nebula/activity/earn/overview/basicInfo?source=bottom_guide_first";
  
  const result = await sendRequest({
    method: "GET",
    url: url,
    headers: {
      "Host": "nebula.kuaishou.com",
      "User-Agent": "kwai-android aegon/3.56.0",
      "Cookie": cookie,
      "Content-Type": "application/x-www-form-urlencoded"
    },
    timeout: 12000
  }, proxyUrl, "账号[" + accountId + "] 获取基本信息");
  
  if (result && result.result === 1 && result.data) {
    return {
      nickname: result.data.userData?.nickname || null,
      totalCoin: result.data.totalCoin ?? null,
      allCash: result.data.allCash ?? null
    };
  }
  
  return null;
}

// 快手广告任务类
class KuaishouAdTask {
  constructor({ index, salt, cookie, nickname = "", proxyUrl = null }) {
    this.index = index;
    this.salt = salt;
    this.cookie = cookie;
    this.nickname = nickname || "账号" + index;
    this.proxyUrl = proxyUrl;
    this.coinLimit = 500000;
    this.coinExceeded = false;
    this.accountColor = getAccountColor(index); // 保存账号颜色
    
    this.extractCookieInfo();
    
    this.headers = {
      "Host": "nebula.kuaishou.com",
      "Connection": "keep-alive",
      "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Lite Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile Safari/537.36",
      "Cookie": this.cookie,
      "content-type": "application/json"
    };
    
    this.taskReportPath = "/rest/r/ad/task/report";
    this.startTime = Date.now();
    this.endTime = this.startTime - 30000;
    this.queryParams = "mod=Xiaomi(MI 11)&appver=" + this.appver + "&egid=" + this.egid + "&did=" + this.did;
    
    // 任务配置
    this.taskConfigs = {
      box: {
        name: "宝箱广告",
        businessId: 606,
        posId: 20346,
        subPageId: 100024064,
        requestSceneType: 1,
        taskType: 1
      },
      look: {
        name: "看广告得金币",
        businessId: 672,
        posId: 24067,
        subPageId: 100026367,
        requestSceneType: 1,
        taskType: 1
      },
      food: {
        name: "饭补广告",
        businessId: 9362,
        posId: 24067,
        subPageId: 100026367,
        requestSceneType: 7,
        taskType: 2
      }
    };
    
    // 任务统计
    this.taskStats = {};
    Object.keys(this.taskConfigs).forEach(taskKey => {
      this.taskStats[taskKey] = {
        success: 0,
        failed: 0,
        totalReward: 0
      };
    });
    
    this.lowRewardStreak = 0;
    this.lowRewardThreshold = 10;
    this.lowRewardLimit = 3;
    this.stopAllTasks = false;
    
    this.taskLimitReached = {};
    Object.keys(this.taskConfigs).forEach(taskKey => {
      this.taskLimitReached[taskKey] = false;
    });
  }
  
  // 检查金币限制
  async checkCoinLimit() {
    try {
      const accountInfo = await getAccountBasicInfo(this.cookie, this.proxyUrl, this.index);
      if (accountInfo && accountInfo.totalCoin) {
        const currentCoin = parseInt(accountInfo.totalCoin);
        if (currentCoin >= this.coinLimit) {
          console.log(this.accountColor("账号[" + this.nickname + "] 金币已达 " + currentCoin + "，超过 " + this.coinLimit + " 阈值，将停止任务"));
          this.coinExceeded = true;
          this.stopAllTasks = true;
          return true;
        }
      }
      return false;
    } catch (error) {
      console.log(this.accountColor("账号[" + this.nickname + "] 金币检查异常: " + error.message));
      return false;
    }
  }
  
  // 提取Cookie信息
  extractCookieInfo() {
    try {
      const egidMatch = this.cookie.match(/egid=([^;]+)/);
      const didMatch = this.cookie.match(/did=([^;]+)/);
      const userIdMatch = this.cookie.match(/userId=([^;]+)/);
      const apiStMatch = this.cookie.match(/kuaishou\.api_st=([^;]+)/);
      const appverMatch = this.cookie.match(/appver=([^;]+)/);
      
      this.egid = egidMatch ? egidMatch[1] : "";
      this.did = didMatch ? didMatch[1] : "";
      this.userId = userIdMatch ? userIdMatch[1] : "";
      this.kuaishouApiSt = apiStMatch ? apiStMatch[1] : "";
      this.appver = appverMatch ? appverMatch[1] : "13.7.20.10468";
      
      if (!this.egid || !this.did) {
        console.log(this.accountColor("账号[" + this.nickname + "] cookie格式可能无 egid 或 did，但继续尝试..."));
      }
    } catch (error) {
      console.log(this.accountColor("账号[" + this.nickname + "] 解析cookie失败: " + error.message));
    }
  }
  
  // 获取任务统计
  getTaskStats() {
    return this.taskStats;
  }
  
  // 打印任务统计
  printTaskStats() {
    console.log(this.accountColor("账号[" + this.nickname + "] 任务执行统计:"));
    for (const [taskKey, stats] of Object.entries(this.taskStats)) {
      const taskName = this.taskConfigs[taskKey].name;
      const rewardText = stats.totalReward + "金币";
      console.log(this.accountColor("  " + taskName + ": 成功" + stats.success + "次, 失败" + stats.failed + "次, 总奖励") + 
        (supportsColor ? colors.red(rewardText) : "☆【" + rewardText + "】☆"));
    }
  }
  
  // 重试操作
  async retryOperation(operation, description, maxRetries = 3, delay = 2000) {
    let attempts = 0;
    let lastError = null;
    
    while (attempts < maxRetries) {
      try {
        const result = await operation();
        if (result) {
          return result;
        }
        lastError = new Error(description + " 返回空结果");
      } catch (error) {
        lastError = error;
        console.log(this.accountColor("账号[" + this.nickname + "] " + description + " 异常: " + error.message));
      }
      
      attempts++;
      if (attempts < maxRetries) {
        console.log(this.accountColor("账号[" + this.nickname + "] " + description + " 失败，重试 " + attempts + "/" + maxRetries));
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    if (isDevMode && lastError) {
      console.log(description + " 最终失败: " + lastError.message);
    }
    
    return null;
  }
  
  // 获取广告信息
  async getAdInfo(taskConfig) {
    try {
      const adPath = "/rest/e/reward/mixed/ad";
      const formData = {
        encData: "|encData|",
        sign: "|sign|",
        cs: "false",
        client_key: "2ac2a76d",
        videoModelCrowdTag: "1_23",
        os: "android",
        "kuaishou.api_st": this.kuaishouApiSt,
        uQaTag: "1##swLdgl:99#ecPp:-9#cmNt:-0#cmHs:-3#cmMnsl:-0"
      };
      
      const queryData = {
        earphoneMode: "1",
        mod: "Xiaomi(23116PN5BC)",
        appver: this.appver,
        isp: "CUCC",
        language: "zh-cn",
        ud: this.userId,
        did_tag: "0",
        net: "WIFI",
        kcv: "1599",
        app: "0",
        kpf: "ANDROID_PHONE",
        ver: "11.6",
        android_os: "0",
        boardPlatform: "pineapple",
        kpn: "NEBULA",
        androidApiLevel: "35",
        country_code: "cn",
        sys: "ANDROID_15",
        sw: "1080",
        sh: "2400",
        abi: "arm64",
        userRecoBit: "0"
      };
      
      const requestBody = {
        appInfo: {
          appId: "kuaishou_nebula",
          name: "快手极速版",
          packageName: "com.kuaishou.nebula",
          version: this.appver,
          versionCode: -1
        },
        deviceInfo: {
          osType: 1,
          osVersion: "15",
          deviceId: this.did,
          screenSize: {
            width: 1080,
            height: 2249
          },
          ftt: ""
        },
        userInfo: {
          userId: this.userId,
          age: 0,
          gender: ""
        },
        impInfo: [{
          pageId: 11101,
          subPageId: taskConfig.subPageId,
          action: 0,
          browseType: 3,
          impExtData: "{}",
          mediaExtData: "{}"
        }]
      };
      
      const encodedBody = Buffer.from(JSON.stringify(requestBody)).toString("base64");
      const signatureResult = await this.generateSignature2(adPath, querystring.stringify({
        ...queryData,
        ...formData
      }), this.salt, encodedBody);
      
      if (!signatureResult) {
        console.log(this.accountColor("账号[" + this.nickname + "] 生成签名失败，无法获取" + taskConfig.name));
        return null;
      }
      
      const finalQueryData = {
        ...queryData,
        sig: signatureResult.sig,
        __NS_sig3: signatureResult.__NS_sig3,
        __NS_xfalcon: "",
        __NStokensig: signatureResult.__NStokensig
      };
      
      formData.encData = signatureResult.encData;
      formData.sign = signatureResult.sign;
      
      const url = "https://api.e.kuaishou.com" + adPath + "?" + querystring.stringify(finalQueryData);
      const result = await sendRequest({
        method: "POST",
        url: url,
        headers: {
          "Host": "api.e.kuaishou.com",
          "User-Agent": "kwai-android aegon/3.56.0",
          "Cookie": "kuaishou_api_st=" + this.kuaishouApiSt
        },
        form: formData,
        timeout: 12000
      }, this.proxyUrl, "账号[" + this.nickname + "] 获取广告");
      
      if (!result) {
        return null;
      }
      
      if (result.errorMsg === "OK" && result.feeds && result.feeds[0] && result.feeds[0].ad) {
        const caption = result.feeds[0].caption || result.feeds[0].ad?.caption || "";
        if (caption) {
          console.log(this.accountColor("账号[" + this.nickname + "] 成功获取到广告信息：") + caption);
        }
        
        const expTag = result.feeds[0].exp_tag || "";
        const llsid = expTag.split("/")[1]?.split("_")?.[0] || "";
        
        return {
          cid: result.feeds[0].ad.creativeId,
          llsid: llsid,
          mediaScene: "video"
        };
      }
      
      return null;
    } catch (error) {
      console.log(this.accountColor("账号[" + this.nickname + "] 获取广告异常: " + error.message));
      return null;
    }
  }
  
  // 生成签名
  async generateSignature(creativeId, llsid, taskKey, taskConfig) {
    try {
      const bizData = JSON.stringify({
        businessId: taskConfig.businessId,
        endTime: this.endTime,
        extParams: "",
        mediaScene: "video",
        neoInfos: [{
          creativeId: creativeId,
          extInfo: "",
          llsid: llsid,
          requestSceneType: taskConfig.requestSceneType,
          taskType: taskConfig.taskType,
          watchExpId: "",
          watchStage: 0
        }],
        pageId: 11101,
        posId: taskConfig.posId,
        reportType: 0,
        sessionId: "",
        startTime: this.startTime,
        subPageId: taskConfig.subPageId
      });
      
      const postData = "bizStr=" + encodeURIComponent(bizData) + "&cs=false&client_key=2ac2a76d";
      const urlData = this.queryParams + "&" + postData;
      
      const signResult = await this.requestSignService({
        urlpath: this.taskReportPath,
        urldata: urlData,
        api_client_salt: this.salt
      }, "账号[" + this.nickname + "] 生成报告签名");
      
      if (!signResult || !signResult.data) {
        return null;
      }
      
      return {
        sig: signResult.data.sig,
        sig3: signResult.data.__NS_sig3,
        sigtoken: signResult.data.__NStokensig,
        post: postData
      };
    } catch (error) {
      console.log(this.accountColor("账号[" + this.nickname + "] 生成签名异常: " + error.message));
      return null;
    }
  }
  
  // 生成签名2
  async generateSignature2(urlPath, urlData, salt, requestString) {
    const signResult = await this.requestSignService({
      urlpath: urlPath,
      urldata: urlData,
      api_client_salt: salt,
      req_str: requestString
    }, "账号[" + this.nickname + "] 生成广告签名");
    
    if (!signResult) {
      return null;
    }
    
    return signResult.data || signResult;
  }
  
  // 提交报告
  async submitReport(sig, sig3, sigtoken, postData, taskKey, taskConfig) {
    try {
      const url = "https://api.e.kuaishou.com" + this.taskReportPath + "?" + 
        (this.queryParams + "&sig=" + sig + "&__NS_sig3=" + sig3 + "&__NS_xfalcon=&__NStokensig=" + sigtoken);
      
      const result = await sendRequest({
        method: "POST",
        url: url,
        headers: {
          "Host": "api.e.kuaishou.cn",
          "User-Agent": "kwai-android aegon/3.56.0",
          "Cookie": this.cookie,
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: postData,
        timeout: 12000
      }, this.proxyUrl, "账号[" + this.nickname + "] 提交任务");
      
      if (!result) {
        return {
          success: false,
          reward: 0
        };
      }
      
      if (result.result === 1) {
        const reward = result.data?.neoAmount || 0;
        const rewardText = reward + "金币奖励！";
        console.log(this.accountColor("账号[" + this.nickname + "] " + taskConfig.name) + 
          (supportsColor ? colors.red(rewardText) : "【" + rewardText + "】"));
        
        if (reward < 1000) {
          this.did = generateKuaishouDid();
          console.log(this.accountColor("账号[" + this.nickname + "] 金币低于阈值,模拟下载应用提升权重！"));
        }
        
        return {
          success: true,
          reward: reward
        };
      }
      
      if ([20107, 20108, 1003, 415].includes(result.result)) {
        console.log(this.accountColor("账号[" + this.nickname + "] " + taskConfig.name + " 已达上限"));
        this.taskLimitReached[taskKey] = true;
        return {
          success: false,
          reward: 0
        };
      }
      
      console.log(this.accountColor("账号[" + this.nickname + "] " + taskConfig.name + " 奖励失败，result=" + result.result));
      
      return {
        success: false,
        reward: 0
      };
    } catch (error) {
      console.log(this.accountColor("账号[" + this.nickname + "] 提交任务异常: " + error.message));
      return {
        success: false,
        reward: 0
      };
    }
  }
  
  // 请求签名服务
  async requestSignService(requestData, description) {
    const cardKey = (process.env.km || "").trim();
    if (!cardKey) {
      return null;
    }
    
    const result = await sendRequest({
      method: "POST",
      url: proxyApiUrl + "?card_key=" + encodeURIComponent(cardKey),
      headers: {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "X-Card-Key": cardKey
      },
      body: JSON.stringify(requestData),
      timeout: 15000
    }, null, description + "（签名服务）");
    
    if (!result) {
      return null;
    }
    
    if (result.success && result.status === "queued" && result.queue_id) {
      const queueResult = await this.pollQueueStatus(result.queue_id);
      if (queueResult && queueResult.success && (queueResult.status === "completed" || queueResult.status === "processed")) {
        return queueResult;
      }
      console.log(this.accountColor("账号[" + this.nickname + "] 签名失败: " + (queueResult?.error || queueResult?.status || "未知")));
      return null;
    }
    
    if (result.success && (!result.status || result.status === "processed" || result.status === "completed")) {
      return result;
    }
    
    console.log(this.accountColor("账号[" + this.nickname + "] 签名失败: " + (result.error || result.message || result.status || "未知")));
    return null;
  }
  
  // 轮询队列状态
  async pollQueueStatus(queueId, maxTime = 30000, interval = 2000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxTime) {
      const result = await sendRequest({
        method: "GET",
        url: queueStatusApiUrl + "?queue_id=" + encodeURIComponent(queueId),
        headers: {
          "User-Agent": "Mozilla/5.0"
        },
        timeout: 10000
      }, null, "账号[" + this.nickname + "] 签名排队");
      
      if (result?.success) {
        if (result.status === "completed" || result.status === "processed") {
          return result;
        }
        if (result.status === "failed") {
          return result;
        }
      }
      
      await new Promise(resolve => setTimeout(resolve, interval));
    }
    
    return {
      success: false,
      status: "failed",
      error: "queue_timeout"
    };
  }
  
  // 执行单个任务
  async executeTask(taskKey) {
    const taskConfig = this.taskConfigs[taskKey];
    if (!taskConfig) {
      console.log(this.accountColor("账号[" + this.nickname + "] 未知任务: " + taskKey));
      return false;
    }
    
    if (this.taskLimitReached[taskKey]) {
      return false;
    }
    
    try {
      const adInfo = await this.retryOperation(() => this.getAdInfo(taskConfig), "获取" + taskConfig.name + "信息", 3);
      if (!adInfo) {
        this.taskStats[taskKey].failed++;
        return false;
      }
      
      const watchTime = Math.floor(Math.random() * 10000) + 30000;
      console.log(this.accountColor("账号[" + this.nickname + "] " + taskConfig.name + " " + generateRandomInteractionMessage() + " " + Math.round(watchTime / 1000) + " 秒"));
      await new Promise(resolve => setTimeout(resolve, watchTime));
      
      const signature = await this.retryOperation(() => this.generateSignature(adInfo.cid, adInfo.llsid, taskKey, taskConfig), "生成" + taskConfig.name + "签名", 3);
      if (!signature) {
        this.taskStats[taskKey].failed++;
        return false;
      }
      
      const submitResult = await this.retryOperation(() => this.submitReport(signature.sig, signature.sig3, signature.sigtoken, signature.post, taskKey, taskConfig), "提交" + taskConfig.name + "报告", 3);
      
      if (submitResult?.success) {
        this.taskStats[taskKey].success++;
        this.taskStats[taskKey].totalReward += submitResult.reward || 0;
        
        if ((submitResult.reward || 0) <= this.lowRewardThreshold) {
          this.lowRewardStreak++;
          if (this.lowRewardStreak >= this.lowRewardLimit) {
            console.log(this.accountColor("账号[" + this.nickname + "] 连续" + this.lowRewardLimit + "次奖励≤" + this.lowRewardThreshold + "，停止全部任务"));
            this.stopAllTasks = true;
          }
        } else {
          this.lowRewardStreak = 0;
        }
        
        return true;
      }
      
      this.taskStats[taskKey].failed++;
      return false;
    } catch (error) {
      console.log(this.accountColor("账号[" + this.nickname + "] 任务异常(" + taskKey + "): " + error.message));
      this.taskStats[taskKey].failed++;
      return false;
    }
  }
  
  // 按优先级执行所有任务
  async executeAllTasksByPriority() {
    const taskKeys = Object.keys(this.taskConfigs);
    const results = {};
    
    for (const taskKey of taskKeys) {
      if (this.stopAllTasks) {
        break;
      }
      
      console.log(this.accountColor("账号[" + this.nickname + "] 开始任务：" + this.taskConfigs[taskKey].name));
      results[taskKey] = await this.executeTask(taskKey);
      
      if (this.stopAllTasks) {
        break;
      }
      
      if (taskKey !== taskKeys[taskKeys.length - 1]) {
        const waitTime = Math.floor(Math.random() * 8000) + 7000;
        console.log(this.accountColor("账号[" + this.nickname + "] 下一个任务，随机等待 " + Math.round(waitTime / 1000) + " 秒"));
        await new Promise(resolve => setTimeout(resolve, waitTime));
      }
    }
    
    return results;
  }
}

// 解析账号配置
function parseAccountConfig(configString) {
  const parts = String(configString || "").trim().split("#");
  if (parts.length < 2) {
    return null;
  }
  
  const cookie = parts[0];
  const salt = parts.slice(1, parts.length - (parts.length >= 3 ? 1 : 0)).join("#");
  let proxyUrl = null;
  
  if (parts.length >= 3) {
    const proxyPart = parts[parts.length - 1].trim();
    
    if (proxyPart.includes("|")) {
      const proxyParts = proxyPart.split("|");
      if (proxyParts.length >= 2) {
        const [ip, port, username, password] = proxyParts;
        proxyUrl = "socks5://" + username + ":" + password + "@" + ip + ":" + port;
      }
    } else {
      proxyUrl = /^socks5:\/\/.+/i.test(proxyPart) ? proxyPart : null;
    }
    
    if (!proxyUrl) {
      console.log("代理字段不是 socks5:// URL，忽略：" + proxyPart);
    }
  }
  
  return {
    salt: salt,
    cookie: cookie,
    proxyUrl: proxyUrl
  };
}

// 从单一ksck环境变量加载账号配置
function loadAccountsFromEnv() {
  const ksckValue = process.env.ksck;
  if (!ksckValue) {
    console.log("未找到 ksck 环境变量");
    return [];
  }
  
  const configStrings = ksckValue.split('&').map(config => config.trim()).filter(Boolean);
  console.log(`从ksck环境变量中解析到 ${configStrings.length} 个配置`);
  
  const accounts = [];
  
  for (const configString of configStrings) {
    const accountConfig = parseAccountConfig(configString);
    if (accountConfig) {
      accounts.push(accountConfig);
    } else {
      console.log("账号格式错误：" + configString);
    }
  }
  
  accounts.forEach((account, index) => {
    account.index = index + 1;
  });
  
  return accounts;
}

// 并发执行
async function concurrentExecute(items, concurrency, processor) {
  const results = new Array(items.length);
  let currentIndex = 0;
  
  async function worker() {
    while (true) {
      const index = currentIndex++;
      if (index >= items.length) {
        return;
      }
      
      const item = items[index];
      try {
        results[index] = await processor(item, index);
      } catch (error) {
        console.log("并发执行异常（index=" + (index + 1) + "）：" + error.message);
        results[index] = null;
      }
    }
  }
  
  const workers = Array.from({ length: Math.min(concurrency, items.length) }, worker);
  await Promise.all(workers);
  
  return results;
}

// 处理单个账号
async function processAccount(accountConfig, maxRounds = 10) {
  const accountColor = getAccountColor(accountConfig.index);
  
  // 代理测试
  if (accountConfig.proxyUrl) {
    console.log(accountColor("账号[" + accountConfig.index + "] 测试代理连接中..."));
    const proxyTest = await testProxyConnectivity(accountConfig.proxyUrl, "账号[" + accountConfig.index + "]");
    console.log(accountColor("  - " + (proxyTest.ok ? "代理验证通过，IP: " + proxyTest.ip : "代理验证失败") + ": " + proxyTest.msg));
    
    if (proxyTest.ok && proxyTest.ip && proxyTest.ip !== "localhost") {
      if (usedProxies.has(proxyTest.ip)) {
        console.log(accountColor("存在相同代理IP（" + proxyTest.ip + "），请立即检查！"));
        process.exit(1);
      }
      usedProxies.add(proxyTest.ip);
    }
  } else {
    console.log(accountColor("账号[" + accountConfig.index + "] 未配置代理，走直连"));
  }
  
  // 获取账号信息
  console.log(accountColor("账号[" + accountConfig.index + "] 获取账号信息中..."));
  let initialAccountInfo = await getAccountBasicInfo(accountConfig.cookie, accountConfig.proxyUrl, accountConfig.index);
  let nickname = initialAccountInfo?.nickname || "账号" + accountConfig.index;
  
  if (initialAccountInfo) {
    const totalCoin = initialAccountInfo.totalCoin != null ? initialAccountInfo.totalCoin : "未知";
    const allCash = initialAccountInfo.allCash != null ? initialAccountInfo.allCash : "未知";
    console.log(accountColor("账号[" + nickname + "] 登录成功，当前金币: " + totalCoin + "，当前余额: " + allCash));
  } else {
    console.log(accountColor("账号[" + nickname + "] 基本信息获取失败，继续执行"));
  }
  
  // 创建任务实例
  const adTask = new KuaishouAdTask({
    ...accountConfig,
    nickname: nickname
  });
  
  // 检查金币限制
  await adTask.checkCoinLimit();
  if (adTask.coinExceeded) {
    console.log(accountColor("账号[" + adTask.nickname + "] 初始金币已超过阈值，不执行任务"));
    
    const finalAccountInfo = await getAccountBasicInfo(accountConfig.cookie, accountConfig.proxyUrl, accountConfig.index);
    const initialCoin = initialAccountInfo?.totalCoin || 0;
    const finalCoin = finalAccountInfo?.totalCoin || 0;
    const coinChange = finalCoin - initialCoin;
    const initialCash = initialAccountInfo?.allCash || 0;
    const finalCash = finalAccountInfo?.allCash || 0;
    const cashChange = finalCash - initialCash;
    
    return {
      index: accountConfig.index,
      nickname: nickname,
      initialCoin: initialCoin,
      finalCoin: finalCoin,
      coinChange: coinChange,
      initialCash: initialCash,
      finalCash: finalCash,
      cashChange: cashChange,
      stats: adTask.getTaskStats(),
      coinLimitExceeded: true
    };
  }
  
  // 执行任务轮次
  for (let round = 0; round < maxRounds; round++) {
    const waitTime = Math.floor(Math.random() * 8000) + 8000;
    console.log(accountColor("账号[" + adTask.nickname + "] 第" + (round + 1) + "轮，先随机等待 " + Math.round(waitTime / 1000) + " 秒"));
    await new Promise(resolve => setTimeout(resolve, waitTime));
    
    console.log(accountColor("账号[" + adTask.nickname + "] 开始第" + (round + 1) + "轮任务"));
    const roundResults = await adTask.executeAllTasksByPriority();
    
    if (Object.values(roundResults).some(Boolean)) {
      console.log(accountColor("账号[" + adTask.nickname + "] 第" + (round + 1) + "轮执行完成"));
    } else {
      console.log(accountColor("账号[" + adTask.nickname + "] 第" + (round + 1) + "轮没有成功任务"));
    }
    
    if (adTask.stopAllTasks) {
      console.log(accountColor("账号[" + adTask.nickname + "] 达到停止条件，终止后续轮次"));
      break;
    }
    
    if (round < maxRounds - 1) {
      const nextWaitTime = Math.floor(Math.random() * 10000) + 10000;
      console.log(accountColor("账号[" + adTask.nickname + "] 等待 " + Math.round(nextWaitTime / 1000) + " 秒进入下一轮"));
      await new Promise(resolve => setTimeout(resolve, nextWaitTime));
    }
  }
  
  // 获取最终信息
  const finalAccountInfo = await getAccountBasicInfo(accountConfig.cookie, accountConfig.proxyUrl, accountConfig.index);
  const initialCoin = initialAccountInfo?.totalCoin || 0;
  const finalCoin = finalAccountInfo?.totalCoin || 0;
  const coinChange = finalCoin - initialCoin;
  const initialCash = initialAccountInfo?.allCash || 0;
  const finalCash = finalAccountInfo?.allCash || 0;
  const cashChange = finalCash - initialCash;
  
  adTask.printTaskStats();
  
  return {
    index: accountConfig.index,
    nickname: nickname,
    initialCoin: initialCoin,
    finalCoin: finalCoin,
    coinChange: coinChange,
    initialCash: initialCash,
    finalCash: finalCash,
    cashChange: cashChange,
    stats: adTask.getTaskStats(),
    coinLimitExceeded: adTask.coinExceeded
  };
}

// 打印账号汇总
function printAccountsSummary(accountResults) {
  if (!accountResults.length) {
    console.log("没有可显示的账号信息。");
    return;
  }
  
  // 计算汇总数据
  const totalInitialCoin = accountResults.reduce((sum, account) => {
    return sum + (parseInt(account.initialCoin) || 0);
  }, 0);
  
  const totalFinalCoin = accountResults.reduce((sum, account) => {
    return sum + (parseInt(account.finalCoin) || 0);
  }, 0);
  
  const totalCoinChange = totalFinalCoin - totalInitialCoin;
  
  const totalInitialCash = accountResults.reduce((sum, account) => {
    return sum + (parseFloat(account.initialCash) || 0);
  }, 0);
  
  const totalFinalCash = accountResults.reduce((sum, account) => {
    return sum + (parseFloat(account.finalCash) || 0);
  }, 0);
  
  const totalCashChange = totalFinalCash - totalInitialCash;
  
  let totalTasks = 0;
  let totalSuccessTasks = 0;
  let totalReward = 0;
  
  accountResults.forEach(account => {
    if (account.stats) {
      Object.values(account.stats).forEach(stat => {
        totalTasks += stat.success + stat.failed;
        totalSuccessTasks += stat.success;
        totalReward += stat.totalReward;
      });
    }
  });
  
  const successRate = totalTasks > 0 ? (totalSuccessTasks / totalTasks * 100).toFixed(1) : "0.0";
  const coinLimitExceededCount = accountResults.filter(account => account.coinLimitExceeded).length;
  
  // 简化汇总输出
  console.log(colors.bold("\n任务执行结果汇总:"));
  console.log("总账号数: " + accountResults.length);
  console.log("超过金币阈值账号: " + coinLimitExceededCount);
  console.log("总任务数: " + totalTasks + "，成功: " + totalSuccessTasks + "，成功率: " + successRate + "%");
  
  const totalRewardText = "总金币变化: " + totalCoinChange + "，总金币奖励: " + totalReward;
  console.log(supportsColor ? colors.red(totalRewardText) : totalRewardText);
  console.log("总余额变化: " + totalCashChange.toFixed(2));
  
  console.log("\n各账号详情:");
  accountResults.forEach(account => {
    const accountColor = getAccountColor(account.index);
    const coinChangeStr = account.coinChange >= 0 ? "+" + account.coinChange : account.coinChange;
    const cashChangeStr = account.cashChange >= 0 ? "+" + account.cashChange.toFixed(2) : account.cashChange.toFixed(2);
    
    const accountInfo = `账号${account.index} [${account.nickname}${account.coinLimitExceeded ? " 超限" : ""}]:` + 
      ` 金币 ${account.initialCoin} -> ${account.finalCoin} (${coinChangeStr}),` + 
      ` 余额 ${account.initialCash} -> ${account.finalCash} (${cashChangeStr})`;
    
    console.log(accountColor(accountInfo));
  });
}

// 主函数
(async () => {
  const accounts = loadAccountsFromEnv();
  console.log("共找到 " + accounts.length + " 个有效账号");
  
  if (!accounts.length) {
    process.exit(1);
  }
  
  const maxConcurrency = parseInt(process.env.MAX_CONCURRENCY || process.env.CONCURRENCY || "8880", 10) || 8888;
  const maxRounds = parseInt(process.env.ROUNDS || "1000", 10) || 1000;
  
  console.log("并发：" + maxConcurrency + "，轮数：" + maxRounds);
  
  const results = [];
  
  await concurrentExecute(accounts, maxConcurrency, async (account) => {
    const accountColor = getAccountColor(account.index);
    console.log(accountColor("\n开始账号[" + account.index + "]"));
    
    try {
      const result = await processAccount(account, maxRounds);
      results.push({
        index: account.index,
        nickname: result?.nickname || this.nickname,
        initialCoin: result?.initialCoin || 0,
        finalCoin: result?.finalCoin || 0,
        coinChange: result?.coinChange || 0,
        initialCash: result?.initialCash || 0,
        finalCash: result?.finalCash || 0,
        cashChange: result?.cashChange || 0,
        stats: result?.stats || {},
        coinLimitExceeded: result?.coinLimitExceeded || false
      });
    } catch (error) {
      const accountColor = getAccountColor(account.index);
      console.log(accountColor("账号[" + account.index + "] 执行异常：" + error.message));
      results.push({
        index: account.index,
        nickname: this.nickname,
        initialCoin: 0,
        finalCoin: 0,
        coinChange: 0,
        initialCash: 0,
        finalCash: 0,
        cashChange: 0,
        error: error.message
      });
    }
  });
  
  results.sort((a, b) => a.index - b.index);
  
  console.log(colors.bold("\n全部完成"));
  printAccountsSummary(results);
})();
// 当前脚本来自于http://script.345yun.cn脚本库下载！