import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import store from './data/store';
import { Provider } from 'react-redux';
import { api } from './api/api';
import { setConfig, setDaemon, setErrorInfo, setRoomStockPlans, setTimetableNodes, setTimetablePeriods, setUser } from './data/action';
import { sleep } from './utils/utils';

// 循环执行函数
async function cycleFunc(cycle = 1000) {
  while (true) {
    try {

    } catch (e) {
      console.error(e);
    }
    await sleep(cycle);
  }
}

// 开始执行的函数
async function startFunc() {
  setTimeout(async () => {
    const user = store.getState().user;
    const isNowLogining = !user && store.getState().config.data.api_token.access_token;
    if (isNowLogining) {
      api.load_from_config();
      const res = await api.request('user', 'GET');
      // console.log('index res', res)
      if (res.code === 200) {
        // console.log('saving user', res.data.user)
        store.dispatch(setUser(res.data.user));
        const daemon = await api.request('daemon', 'GET');
        if (daemon.code === 200 && daemon.data.uid) {
          store.dispatch(setDaemon(daemon.data));
        } else store.dispatch(setDaemon(null));
      }
    }
    // let c = api.download_config();
    // if (!c.settings_async) return;
    // const config_frontend = await api.download_config();
    // if (!config_frontend) {
    //   store.dispatch(setErrorInfo("同步设置失败"));
    // }
    // else store.dispatch(setConfig(config_frontend));
  }, 0);
}

ReactDOM.render(
  // <React.StrictMode>
  <Provider store={store}>
    <App />
  </Provider>,
  // </React.StrictMode>,
  document.getElementById('root')
);

startFunc().then(() => {
  cycleFunc();
});

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
