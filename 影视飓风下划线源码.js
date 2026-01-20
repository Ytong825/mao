// 当前脚本来自于 http://script.345yun.cn 脚本库下载！
// 脚本库官方QQ群: 429274456
// 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
// 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
// 您在使用脚本库下载的脚本时自行检查判断风险。
// 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。

/**
 * 环境变量：YSJFCS，格式为：
 *  账号1+++token1+++sid1
 *  账号2+++token2+++sid2
 *  （每行一个账号，回车分割，仅需备注+token+sid）
 */
const axios = require('axios');
const https = require('https');

// ===================== 【全局配置区】可根据需求调整 =====================
const CONFIG = {
    // 版本检测配置
    version: {
        local: "1.0.1", // 本地版本号
        checkUrl: "http://43.138.107.29:39990/bbjc/wxyd", // 版本检测地址
        timeout: 5000 // 版本检测请求超时时间
    },
    // 接口地址
    getActivityUrl: 'https://h5.youzan.com/wscump/checkin/get_activity_by_yzuid_v2.json',
    checkinUrl: 'https://h5.youzan.com/wscump/checkin/checkinV2.json',
    memberCenterUrl: 'https://h5.youzan.com/wscuser/membercenter/init-data.json',
    // 请求配置
    timeout: 15000, // 业务请求超时时间
    retryTimes: 2, // 重试次数
    retryDelay: 1000, // 重试间隔
    // 固定参数
    checkinId: '6287727',
    appId: 'wx92782ef90ebc836d',
    kdtId: '149536603',
    referer: 'https://servicewechat.com/wx92782ef90ebc836d/16/page-frame.html',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541510) XWEB/17071',
   
    extraDataBase: {
        is_weapp: 1,
        version: '2.210.8.101',
        client: 'weapp',
        bizEnv: 'wsc',
        uuid: 'syI8nUxdYOT50im1766025528226'
    },
    // 会员中心接口固定参数
    memberCenterParams: {
        version: '2.210.8.101',
        kdtId: '149536603',
        onlineKdtId: '149536603',
        currentKdtId: '149536603',
        needConsumptionAboveCoupon: '1'
    },
    // 日志配置
    log: {
        isDeveloperMode: false, 
        prefixes: {
            success: '[SUCCESS]',
            info: '[INFO]',
            warn: '[WARN]',
            error: '[ERROR]'
        }
    }
};
// ===================== 配置结束 =====================

// 创建axios实例（忽略SSL警告）
const axiosInstance = axios.create({
    timeout: CONFIG.timeout,
    headers: {
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    },
    decompress: true,
    httpsAgent: new https.Agent({ rejectUnauthorized: false })
});

// 创建版本检测专用axios实例（独立超时配置）
const versionAxios = axios.create({
    timeout: CONFIG.version.timeout,
    headers: {
        'Content-Type': 'application/json'
    }
});

// ===================== 日志工具 =====================
function log(type, message, isDeveloperLog = false) {
    const { prefixes, isDeveloperMode } = CONFIG.log;
    if (isDeveloperLog && !isDeveloperMode) return;
    const validType = ['success', 'info', 'warn', 'error'].includes(type) ? type : 'info';
    const prefix = prefixes[validType];
    console.log(`${prefix} ${message}`);
}

const logger = {
    userSuccess: (msg) => log('success', msg, false),
    userInfo: (msg) => log('info', msg, false),
    userWarn: (msg) => log('warn', msg, false),
    userError: (msg) => log('error', msg, false),
    devSuccess: (msg) => log('success', msg, true),
    devInfo: (msg) => log('info', msg, true),
    devWarn: (msg) => log('warn', msg, true),
    devError: (msg) => log('error', msg, true)
};

// ===================== 版本检测函数（核心新增） =====================
/**
 * 版本检测函数：请求远程版本，与本地对比，不一致则退出
 */
async function checkVersion() {
    logger.userInfo('开始执行版本检测...');
    try {
        // 发送GET请求获取远程版本
        const response = await versionAxios.get(CONFIG.version.checkUrl);
        const remoteVersion = response.data?.version;
        
        // 开发者日志打印完整响应
        logger.devInfo(`版本检测响应：${JSON.stringify(response.data)}`);

        if (!remoteVersion) {
            logger.userError('远程版本信息获取失败，响应无version字段QQ群1073504990');
            process.exit(1);
        }

        // 版本对比
        if (remoteVersion === CONFIG.version.local) {
            logger.userSuccess(`版本检测通过：本地版本 ${CONFIG.version.local} | 远程版本 ${remoteVersion}    QQ群1073504990`);
        } else {
            logger.userError(`版本不一致，脚本退出！本地版本 ${CONFIG.version.local} | 远程版本 ${remoteVersion}      QQ群1073504990`);
            process.exit(1);
        }
    } catch (error) {
        logger.userError(`版本检测请求失败：${error.message   }QQ群1073504990`);
        logger.devError(`版本检测失败详情：${error.stack}      QQ群1073504990`);
        process.exit(1);
    }
}

// ===================== 工具函数 =====================
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function parseYSJFCSConfig() {
    const configList = [];
    const ysjfcs = process.env.YSJFCS || '';
    if (!ysjfcs) {
        logger.userError('未配置环境变量YSJFCS，脚本终止执行');
        return [];
    }

    const lines = ysjfcs.split(/\r?\n|\r/).filter(line => line.trim());
    if (lines.length === 0) {
        logger.userError('YSJFCS环境变量中无有效账号配置，脚本终止执行');
        return [];
    }

    lines.forEach((line, index) => {
        const lineNum = index + 1;
        const parts = line.split('+++').map(part => part.trim());
        if (parts.length !== 3) {
            logger.userWarn(`第${lineNum}行格式错误，需为 备注+++token+++sid，跳过该行`);
            return;
        }

        const [remark, accessToken, sid] = parts;
        if (!remark || !accessToken || !sid) {
            logger.userWarn(`第${lineNum}行参数为空，跳过该行`);
            return;
        }

        logger.devInfo(`解析账号${lineNum}：${remark}`);
        configList.push({
            remark,
            accessToken,
            sid,
            uuid: CONFIG.extraDataBase.uuid
        });
    });

    return configList;
}

// ===================== 前置操作函数 =====================
function preCheckinAction1(config) {
    logger.devInfo(`【参数校验】开始校验${config.remark}参数`);
    const tokenValid = /^[0-9a-fA-F]+$/.test(config.accessToken);
    const sidValid = config.sid.startsWith('YZ') && config.sid.includes('YZ');

    if (tokenValid && sidValid) {
        logger.devSuccess(`【参数校验】${config.remark}参数校验通过`);
        return true;
    } else {
        logger.userWarn(`${config.remark}参数校验失败，跳过该账号`);
        logger.devWarn(`【参数校验】失败详情：token=${tokenValid}, sid=${sidValid}`);
        return false;
    }
}

function preCheckinAction2(config) {
    logger.devInfo(`【参数摘要】${config.remark}：`);
    const tokenDesensitized = `${config.accessToken.substring(0, 8)}****${config.accessToken.slice(-8)}`;
    const sidDesensitized = `${config.sid.substring(0, 10)}****${config.sid.slice(-10)}`;
    logger.devInfo(`  - accessToken：${tokenDesensitized}`);
    logger.devInfo(`  - sid：${sidDesensitized}`);
}

// ===================== 核心请求函数 =====================
function buildRequestConfig(userConfig, url, extraParams = {}) {
    const currentFtime = Date.now();
    const extraData = {
        ...CONFIG.extraDataBase,
        sid: userConfig.sid,
        uuid: userConfig.uuid,
        ftime: currentFtime
    };
    const baseParams = {
        checkinId: CONFIG.checkinId,
        app_id: CONFIG.appId,
        kdt_id: CONFIG.kdtId,
        access_token: userConfig.accessToken
    };
    const params = { ...baseParams, ...extraParams };
    const headers = {
        'Host': 'h5.youzan.com',
        'Connection': 'keep-alive',
        'User-Agent': CONFIG.userAgent,
        'xweb_xhr': '1',
        'Content-Type': 'application/json',
        'Extra-Data': JSON.stringify(extraData),
        'Accept': '*/*',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': CONFIG.referer,
        'Accept-Language': 'zh-CN,zh;q=0.9'
    };

    logger.devInfo(`构造请求：URL=${url}`);
    return { url, params, headers };
}

async function sendRequest(requestConfig, actionName, retry = 0) {
    try {
        const response = await axiosInstance.get(requestConfig.url, {
            params: requestConfig.params,
            headers: requestConfig.headers
        });
        logger.devSuccess(`${actionName}成功，状态码：${response.status}`);
        return { statusCode: response.status, body: response.data };
    } catch (error) {
        const errorMsg = error.response
            ? `${actionName}失败（状态码：${error.response.status}）：${JSON.stringify(error.response.data)}`
            : `${actionName}失败：${error.message}`;

        if (retry < CONFIG.retryTimes) {
            logger.devWarn(`${errorMsg}，${CONFIG.retryDelay}ms后重试（第${retry + 1}次）`);
            await delay(CONFIG.retryDelay);
            return sendRequest(requestConfig, actionName, retry + 1);
        }
        logger.devError(`${actionName}最终失败：${errorMsg}`);
        throw new Error(errorMsg);
    }
}

async function getActivity(userConfig) {
    const requestConfig = buildRequestConfig(userConfig, CONFIG.getActivityUrl);
    return sendRequest(requestConfig, '获取活动信息');
}

async function doCheckin(userConfig) {
    const requestConfig = buildRequestConfig(userConfig, CONFIG.checkinUrl);
    return sendRequest(requestConfig, '签到');
}

async function getMemberPoints(userConfig) {
    const memberParams = {
        ...CONFIG.memberCenterParams,
        kdt_id: CONFIG.kdtId,
        app_id: CONFIG.appId,
        access_token: userConfig.accessToken
    };
    const requestConfig = buildRequestConfig(userConfig, CONFIG.memberCenterUrl, memberParams);
    return sendRequest(requestConfig, '查询会员积分');
}

function parsePointsBalance(pointsResult) {
    const points = pointsResult.body?.data?.member?.stats?.points || 0;
    logger.devInfo(`会员积分详情：${points} 积分`);
    return points;
}

// ===================== 主函数 =====================
async function main() {
    // 第一步：执行版本检测，不通过则直接退出
    await checkVersion();

    logger.userInfo('========== 有赞签到脚本开始执行 ==========');
    const userConfigList = parseYSJFCSConfig();
    if (userConfigList.length === 0) {
        logger.userError('无有效账号配置，脚本终止执行');
        return;
    }
    logger.userSuccess(`共解析到${userConfigList.length}个有效账号，开始处理`);

    for (let index = 0; index < userConfigList.length; index++) {
        const config = userConfigList[index];
        const accountNum = index + 1;
        logger.userInfo(`\n========== 处理第${accountNum}个账号：${config.remark} ==========`);

        try {
            if (!preCheckinAction1(config)) continue;
            preCheckinAction2(config);

            // 签到前积分查询
            const prePointsResult = await getMemberPoints(config);
            const prePoints = parsePointsBalance(prePointsResult);
            logger.userInfo(`${config.remark} - 签到前积分：${prePoints} 积分`);

            // 获取活动信息
            await getActivity(config);

            // 执行签到
            const checkinResult = await doCheckin(config);
            if (checkinResult.body.code === 0 || checkinResult.body.success) {
                logger.userSuccess(`${config.remark} - 签到成功！`);
            } else {
                logger.userWarn(`${config.remark} - 签到失败：${checkinResult.body.msg || '未知原因'}`);
            }

            // 签到后积分查询
            const postPointsResult = await getMemberPoints(config);
            const postPoints = parsePointsBalance(postPointsResult);
            logger.userInfo(`${config.remark} - 签到后积分：${postPoints} 积分`);

            // 积分变化
            const pointsChange = postPoints - prePoints;
            if (pointsChange > 0) {
                logger.userSuccess(`${config.remark} - 积分增加${pointsChange}分！`);
            } else if (pointsChange < 0) {
                logger.userWarn(`${config.remark} - 积分减少${Math.abs(pointsChange)}分`);
            } else {
                logger.userInfo(`${config.remark} - 积分无变化`);
            }
        } catch (error) {
            logger.userError(`${config.remark} - 处理失败：${error.message}`);
            logger.devError(`失败详情：${error.stack}`);
        }
    }

    logger.userInfo('\n========== 有赞签到脚本执行完毕 ==========');
}

// 启动脚本
main().catch(error => {
    logger.userError(`脚本执行异常：${error.message}`);
    logger.devError(`异常详情：${error.stack}`);
    process.exit(1);
});

// 当前脚本来自于 http://script.345yun.cn 脚本库下载！
// 脚本库官方QQ群: 429274456
// 脚本库中的所有脚本文件均来自热心网友上传和互联网收集。
// 脚本库仅提供文件上传和下载服务，不提供脚本文件的审核。
// 您在使用脚本库下载的脚本时自行检查判断风险。
// 所涉及到的 账号安全、数据泄露、设备故障、软件违规封禁、财产损失等问题及法律风险，与脚本库无关！均由开发者、上传者、使用者自行承担。