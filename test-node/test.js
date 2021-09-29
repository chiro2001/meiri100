// const fetch = require('node-fetch');
import fetch from "node-fetch";

const test_main = async () => {
  const login_resp = await fetch("http://yqdz.meiri100.cn/login/login_ok", {
    "credentials": "include",
    "headers": {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
      "Accept": "application/json, text/javascript, */*; q=0.01",
      "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      "X-Requested-With": "XMLHttpRequest",
      "Pragma": "no-cache",
      "Cache-Control": "no-cache"
    },
    "referrer": "http://yqdz.meiri100.cn/login/index",
    "body": "username=16650216792&password=wangyamin202",
    "method": "POST",
    "mode": "cors"
  });
  console.log('login_resp', login_resp);
};

test_main();