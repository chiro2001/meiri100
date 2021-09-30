import { Box, Button, Container, Divider, TextField, Typography, Zoom, Fade } from '@material-ui/core';
import React from 'react';
import { api } from '../api/api';
import { setMessage, setUser } from '../data/action';
import store from '../data/store';
import { objectUpdate } from '../utils/utils';


function LoginFrame(props) {
  const [state, setInnerState] = React.useState({
    username: "",
    password: "",
    vip_code: "",
    email: '',
    actionType: 'login'
  });
  const refUsername = React.useRef();
  const refPassword = React.useRef();
  const refEmail = React.useRef();
  const refVipCode = React.useRef();
  const setState = (update) => setInnerState(objectUpdate(state, update));
  // style={{ display: "flex", justifyContent: 'center', alignItems: "center", flexDirection: "column", }}
  const actionLogin = state.actionType === 'login' ? true : false;
  const handleAction = async () => {
    // console.log('handle', actionLogin);
    if (actionLogin) {
      const res = await api.request('session', 'POST', {
        username: state.username, password: state.password
      });
      console.log(res);
      if (res.code !== 200) return;
      // 获取user
      const user = await api.request('user', 'GET');
      if (user.code !== 200) return;
      console.log('user', user.data.user);
      store.dispatch(setUser(user.data.user));
    } else {
      // 注册，注册成功则跳转登录
      const res = await api.request('user', 'POST', {
        username: state.username, password: state.password, vip_code: state.vip_code, email: state.email
      });
      console.log(res);
      if (res.code === 200) {
        // 弹窗
        store.dispatch(setMessage("注册成功"));
        setState({ actionType: 'login' });
      }
    }
  }

  return (<Box>
    <Typography variant="h4">{actionLogin ? "登录" : "注册"}</Typography>
    <br />
    <Divider></Divider>
    <br />
    <TextField fullWidth ref={refUsername} label="用户名" variant="outlined" value={state.username} onChange={e => {
      setState({ username: e.target.value });
    }} onKeyDown={e => {
      if (e.code === "Enter") {
        refPassword.current.querySelector("input").focus();
      }
    }} />
    <br /><br />
    <TextField fullWidth ref={refPassword} label="密码" variant="outlined" value={state.password} type="password" onChange={e => {
      setState({ password: e.target.value });
    }} onKeyDown={e => {
      if (e.code === "Enter") {
        if (actionLogin) {
          handleAction();
        } else {
          refEmail.current.querySelector("input").focus();
        }
      }
    }} />
    <br /><br />
    {actionLogin ? null : <>
      <TextField fullWidth ref={refEmail} label="邮箱, 用于接收程序消息" variant="outlined" value={state.email} onChange={e => {
        setState({ email: e.target.value });
      }} onKeyDown={e => {
        if (e.code === "Enter") {
          refVipCode.current.querySelector("input").focus();
        }
      }} /><br /><br />
      <TextField fullWidth ref={refVipCode} label="验证码" variant="outlined" value={state.vip_code} onChange={e => {
        setState({ vip_code: e.target.value });
      }} onKeyDown={e => {
        if (e.code === "Enter") {
          handleAction();
        }
      }} /></>}
    <Fade in={actionLogin} style={{ display: actionLogin ? "block" : "none" }} timeout={{ exit: 0, enter: 200 }}>
      <Box>
        <Box>
          <br></br>
          <Button fullWidth variant="contained" color="primary" onClick={handleAction}>登录</Button>
        </Box>
        <Box>
          <br></br>
          <Button fullWidth variant="contained" color="secondary" onClick={() => setState({ actionType: "sign_in" })}>注册</Button>
        </Box>
      </Box>
    </Fade>
    <Fade in={!actionLogin} style={{ display: !actionLogin ? "block" : "none" }} timeout={{ exit: 0, enter: 200 }}>
      <Box>
        <Box>
          <br></br>
          <Button fullWidth variant="contained" color="primary" onClick={handleAction}>注册</Button>
        </Box>
        <Box>
          <br></br>
          <Button fullWidth variant="contained" onClick={() => setState({ actionType: 'login' })}>返回登录</Button>
        </Box>
      </Box>
    </Fade>
  </Box >);
}

export default function Login(props) {
  return <Container maxWidth="sm">
    <LoginFrame></LoginFrame>
  </Container>
}