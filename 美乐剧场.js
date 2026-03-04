// 环境变量 格式如下：
// 变量名称 mljc
// 变量值 每个账号由 Authorization 和 User-Agent 组成，中间用 & 连接
// 多个账号之间用 # 分隔
// 即：auth1&ua1#auth2&ua2#auth3&ua3

const axios = require('axios');
const crypto = require('crypto');
const https = require('https');

const SIGN_KEY = "nEs^sksaDvFJE8@#H!Stj7&1pMGvrBCc";
const APP_ID = "app003";
const FIXED_DURATION = 60004;
const AD_POINTS_RANGE = [200000, 500000];
const EXCHANGE_INTERVAL = 0;
const MAX_LOOP = 1000;

const URLS = {
  video_report: "https://sdk.xjdy2024.com/api/user/watch-duration/report",
  ad_report: "https://sdk.xjdy2024.com/api/user/report-points",
  exchange: "https://sdk.xjdy2024.com/api/user/exchange-coins",
  treasure: "https://sdk.xjdy2024.com/api/activity/progress?activity_code=cooldown_treasure_box&action=claim",
  red_envelope: "https://sdk.xjdy2024.com/api/activity/progress?activity_code=red_envelope_rain&action=claim"
};

function getAccounts() {
  const mljc = process.env.mljc;
  if (!mljc) {
    console.log("⚠️ 未配置mljc环境变量");
    return [];
  }
  const accounts = [];
  const items = mljc.split('#');
  for (let i = 0; i < items.length; i++) {
    const parts = items[i].split('&');
    if (parts.length !== 2) {
      console.log(`❌ 账号${i+1}格式错误`);
      continue;
    }
    accounts.push({
      idx: i+1,
      auth: parts[0].trim(),
      ua: parts[1].trim()
    });
  }
  return accounts;
}

function genSign(content) {
  return crypto.createHash('sha256').update(content).digest('hex').toLowerCase();
}

async function redEnvelopeTask(account) {
  const { idx, auth, ua } = account;
  const headers = {
    Authorization: auth,
    'User-Agent': ua,
    Origin: 'https://sdk-h5.xjdy2024.com',
    'X-Requested-With': 'com.leguo.life'
  };
  try {
    const response = await axios.get(URLS.red_envelope, { headers, timeout: 15000, httpsAgent: new https.Agent({ rejectUnauthorized: false }) });
    if (response.status === 200 && response.data.success) {
      const data = response.data.result.treasure_box_data;
      console.log(`🧧 账号${idx} 红包雨：${data.coins_gained}金币 | 等待${data.remaining_seconds}秒`);
    } else {
      console.log(`❌ 账号${idx} 红包雨领取失败`);
    }
  } catch (e) {
    console.log(`❌ 账号${idx} 红包雨异常：${e.message.substring(0,15)}`);
  }
}

async function treasureTask(account) {
  const { idx, auth, ua } = account;
  const headers = { Authorization: auth, 'User-Agent': ua };
  try {
    const response = await axios.get(URLS.treasure, { headers, timeout: 15000, httpsAgent: new https.Agent({ rejectUnauthorized: false }) });
    if (response.status === 200 && response.data.success) {
      const data = response.data.result.treasure_box_data;
      console.log(`🎁 账号${idx} 宝箱：${data.coins_gained}金币`);
    } else {
      console.log(`❌ 账号${idx} 宝箱领取失败`);
    }
  } catch (e) {
    console.log(`❌ 账号${idx} 宝箱异常：${e.message.substring(0,15)}`);
  }
}

function startVideoReport(account, runningRef) {
  const { idx, auth, ua } = account;
  const headers = {
    Authorization: auth,
    'X-App-Id': APP_ID,
    'User-Agent': ua,
    'Content-Type': 'application/json'
  };
  const run = async () => {
    if (!runningRef.running) return;
    try {
      const ts = Date.now().toString();
      const jsonStr = JSON.stringify({
        watch_type: "short_drama",
        action_id: ts,
        duration: FIXED_DURATION
      });
      const sign = genSign(`${APP_ID}${ts}${jsonStr}${SIGN_KEY}`);
      headers['X-Signature'] = sign;
      const response = await axios.post(URLS.video_report, jsonStr, { headers, timeout: 15000, httpsAgent: new https.Agent({ rejectUnauthorized: false }) });
      if (response.status === 200 && response.data.success) {
        console.log(`📺 账号${idx} 视频上报成功`);
      } else {
        console.log(`❌ 账号${idx} 视频上报失败`);
      }
    } catch (e) {
      console.log(`❌ 账号${idx} 视频上报异常：${e.message.substring(0,15)}`);
    } finally {
      if (runningRef.running) {
        setTimeout(run, 60000);
      }
    }
  };
  run();
}

function startAdReport(account, runningRef) {
  const { idx, auth, ua } = account;
  const headers = {
    Authorization: auth,
    'X-App-Id': APP_ID,
    'User-Agent': ua,
    'Content-Type': 'application/json'
  };
  const run = async () => {
    if (!runningRef.running) return;
    try {
      const ts = Date.now().toString();
      const ad_points = Math.floor(Math.random() * (AD_POINTS_RANGE[1] - AD_POINTS_RANGE[0] + 1)) + AD_POINTS_RANGE[0];
      const jsonStr = JSON.stringify({
        ad_points: ad_points,
        ad_type: "incentive",
        remark: "激励广告",
        action_id: ts
      });
      const sign = genSign(`${APP_ID}${ts}${jsonStr}${SIGN_KEY}`);
      headers['X-Signature'] = sign;
      const response = await axios.post(URLS.ad_report, jsonStr, { headers, timeout: 15000, httpsAgent: new https.Agent({ rejectUnauthorized: false }) });
      if (response.status === 200 && response.data.success) {
        console.log(`📊 账号${idx} 广告上报：${ad_points}积分`);
      } else {
        console.log(`❌ 账号${idx} 广告上报失败`);
      }
    } catch (e) {
      console.log(`❌ 账号${idx} 广告上报异常：${e.message.substring(0,15)}`);
    } finally {
      if (runningRef.running) {
        const delay = Math.floor(Math.random() * 6 + 5) * 1000;
        setTimeout(run, delay);
      }
    }
  };
  run();
}

function startExchange(account, runningRef) {
  const { idx, auth, ua } = account;
  const headers = {
    Authorization: auth,
    'User-Agent': ua,
    'Content-Type': 'application/json'
  };
  let loopCount = 1;
  const run = async () => {
    if (!runningRef.running || loopCount > MAX_LOOP) {
      if (loopCount > MAX_LOOP) console.log(`🔚 账号${idx} 兑换任务结束`);
      return;
    }
    try {
      const response = await axios.post(URLS.exchange, { source_type: "points", watch_type: "" }, { headers, timeout: 15000, httpsAgent: new https.Agent({ rejectUnauthorized: false }) });
      if (response.status === 200 && response.data.success) {
        const data = response.data.result;
        console.log(`🎉 账号${idx} 兑换${loopCount}：${data.coins_gained}金币 | 剩余${data.current_points}积分`);
      } else {
        console.log(`❌ 账号${idx} 兑换${loopCount}失败`);
      }
    } catch (e) {
      console.log(`❌ 账号${idx} 兑换${loopCount}异常：${e.message.substring(0,15)}`);
    } finally {
      loopCount++;
      if (runningRef.running && loopCount <= MAX_LOOP) {
        setTimeout(run, EXCHANGE_INTERVAL * 1000);
      }
    }
  };
  run();
}

async function main() {
  const accounts = getAccounts();
  if (accounts.length === 0) {
    console.log("❌ 无有效账号，退出");
    return;
  }

  console.log(`📌 检测到${accounts.length}个账号 | 所有任务并行启动`);

  const running = { running: true };

  for (const account of accounts) {
    redEnvelopeTask(account);
    treasureTask(account);
    startVideoReport(account, running);
    startAdReport(account, running);
    startExchange(account, running);
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  console.log("\n✅ 所有任务已并行启动 | 按Ctrl+C停止");

  process.on('SIGINT', () => {
    console.log("\n🛑 脚本停止，所有线程将退出");
    running.running = false;
    setTimeout(() => process.exit(0), 3000);
  });
}

main();