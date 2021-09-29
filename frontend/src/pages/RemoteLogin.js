import { Box, TextField, Button, Container, Paper, Typography } from '@material-ui/core';
import React from 'react';
import { api } from '../api/api';
import Config from "../Config";
import { WebSocketAPI } from '../api/remote_login';
import { setConfig, setDaemon } from '../data/action';
import store from '../data/store';
const QRCode = require('qrcode.react');

function CenterBox(props) {
  const { children, style } = props;
  return <Box style={style ? style : { width: '100%', height: '100%', display: "flex", justifyContent: "center", flexDirection: "column" }}>
    <Box style={{ width: '100%', textAlign: "center", display: "flex", justifyContent: "center", flexDirection: "column", alignItems: "center" }}>
      {children}
    </Box>
  </Box>;
}

export default class RemoteLogin extends React.Component {
  constructor(props) {
    super(props);
    this.onFinish = props.onFinish;
    this.forceLogin = props.forceLogin;
    this.stateDefault = {
      // code: null,
      loginDone: false,
      loginError: null,
      username: "",
      password: ""
    };
    this.refUsername = React.createRef();
    this.refPassword = React.createRef();

    this.state = this.stateDefault;
    this.handleAction = this.handleAction.bind(this);
    // this.ws_api = null;
    // this.ws_running = false;
    // this.unsubscribe = store.subscribe(async () => {
    //   if (this.loginDone) return;
    //   let state = store.getState();
    //   if (state.daemon) {
    //     this.setState({ loginDone: true });
    //     if (this.ws_api) this.ws_api.close();
    //   }
    // });
    // this.run_ws = async () => {
    //   // debugger;
    //   this.ws_running = true;
    //   console.log(store.getState().daemon);
    //   if (!this.forceLogin && ((store.getState().daemon && store.getState().daemon.cookies) || this.state.loginDone)) { this.ws_running = false; return; }
    //   const res = await api.request('remote_login', "PATCH");
    //   if (!this.forceLogin && ((store.getState().daemon && store.getState().daemon.cookies) || this.state.loginDone)) { this.ws_running = false; return; }
    //   const server = res.data.server;
    //   let config = store.getState().config;
    //   config.data.remote_login.server = server;
    //   store.dispatch(setConfig(config));
    //   if (!this.forceLogin && ((store.getState().daemon && store.getState().daemon.cookies) || this.state.loginDone)) { this.ws_running = false; return; }
    //   this.ws_api = new WebSocketAPI(server);
    //   this.ws_api.oncode = code => {
    //     // console.log('code', code);
    //     if (!this.forceLogin && ((store.getState().daemon && store.getState().daemon.cookies) || this.state.loginDone)) { this.ws_running = false; return; }
    //     this.setState({ code });
    //   };
    //   this.ws_api.oncookies = async cookies => {
    //     const resp = await api.request('remote_login', "POST", { cookies });
    //     if (resp.code !== 200) {
    //       this.setState({ loginDone: true, loginError: resp.message });
    //       return;
    //     }
    //     console.log('done', resp);
    //     if (!this.forceLogin && ((store.getState().daemon && store.getState().daemon.cookies) || this.state.loginDone)) { this.ws_running = false; return; }
    //     this.setState({ loginDone: true });
    //     const daemon = await api.request('remote_login', 'GET');
    //     if (daemon.code === 200 && daemon.data.uid) {
    //       store.dispatch(setDaemon(daemon.data));
    //     }
    //     this.onFinish && this.onFinish();
    //   }
    //   if (!this.forceLogin && ((store.getState().daemon && store.getState().daemon.cookies) || this.state.loginDone)) { this.ws_running = false; return; }
    //   this.ws_api.connect();
    // };
    // setTimeout(this.run_ws, 1000);
  }

  componentWillUnmount() {
    // if (this.ws_api) this.ws_api.close();
    // this.unsubscribe();
  }
  async handleAction() {
    const resp = await api.request('remote_login', "POST", {
      username: this.state.username,
      password: this.state.password
    });
    if (resp.code !== 200) {
      this.setState({ loginDone: true, loginError: resp.message });
      return;
    }
    console.log('done remote_login', resp);
    const resp2 = await api.request('remote_login', "POST", {cookies: resp.data.remote_login_result.cookies});
    if (resp2.code !== 200) {
      this.setState({ loginDone: true, loginError: resp.message });
      return;
    }
    console.log('done remote_login post cookies', resp2);
    // if (!this.forceLogin && ((store.getState().daemon && store.getState().daemon.cookies) || this.state.loginDone)) { this.ws_running = false; return; }
    this.setState({ loginDone: true });
    const daemon = await api.request('remote_login', 'GET');
    if (daemon.code === 200 && daemon.data.uid) {
      store.dispatch(setDaemon(daemon.data));
    }
    this.onFinish && this.onFinish();
  }
  // if(!this.forceLogin && ((store.getState().daemon && store.getState().daemon.cookies) || this.state.loginDone)) { this.ws_running = false; return; }
  render() {
    let content = null;
    if (this.state.loginDone) {
      if (!this.state.loginError)
        content = <Paper style={{ width: 200, height: 200 }}>
          <CenterBox>登录完成</CenterBox>
        </Paper>;
      else content = <Paper style={{ width: 200, height: 200 }}>
        <CenterBox>
          <Typography variant="body1">{this.state.loginError}</Typography>
          <Button variant="outlined" color="secondary" onClick={() => {
            // try { clearTimeout(this.run_ws); } catch (e) { console.error(e); }
            // this.setState(this.stateDefault);
            // try { if (this.ws_api) this.ws_api.connect(); } catch (e) { console.error(e); }
            // this.ws_api = null;
            // this.ws_running = false;
            // setTimeout(this.run_ws, 1000);
          }}>重试</Button>
        </CenterBox>
      </Paper>;
    } else {
      // content = this.state.code ? <QRCode value={JSON.stringify(this.state.code)} size={200} /> :
      //   <Paper style={{ width: 200, height: 200 }}>
      //     <CenterBox>正在加载...</CenterBox>
      //   </Paper>;
      content = <div><TextField fullWidth ref={this.refUsername} label="用户名" value={this.state.username} onChange={e => {
        this.setState({ username: e.target.value });
      }} onKeyDown={e => {
        if (e.code === "Enter") {
          this.refPassword.current.querySelector("input").focus();
        }
      }} />
        <br /><br />
        <TextField fullWidth ref={this.refPassword} label="密码" value={this.state.password} type="password" onChange={e => {
          this.setState({ password: e.target.value });
        }} onKeyDown={e => {
          if (e.code === "Enter") {
            this.handleAction();
          }
        }} /> <br /><br />
        <Button fullWidth onClick={() => { this.handleAction(); }} variant="contained" color="primary">验证</Button></div>;
    }
    return (<Container maxWidth="xs" style={{ height: window.innerHeight * 0.6 }}>
      <CenterBox>
        <Typography variant="h5">添加被控制账号</Typography>
        <br></br>
        {content}
        <br></br>
        <Typography variant="body2" color="textSecondary">输入需要控制的账号和密码</Typography>
        <Typography variant="body2" color="textSecondary">本程序将会帮助你抢到重要任务</Typography>
        <br></br>
        <Button fullWidth onClick={() => {
          Config.clear();
          setTimeout(() => { window.location.reload(); }, 500);
        }}>退出当前本网站账号</Button>
      </CenterBox>
    </Container>);
  }
}