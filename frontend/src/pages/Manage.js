
import { Box, Button, CircularProgress, Container, Dialog, DialogActions, DialogContent, DialogTitle, Grid, IconButton, LinearProgress, List, ListItem, ListItemSecondaryAction, ListItemText, ListSubheader, TextField, Typography } from "@material-ui/core";
import DeleteIcon from '@material-ui/icons/Delete';
import React from "react";
import { api } from "../api/api";
import { setConfig, setErrorInfo, setMessage, setAccounts, updateTypes } from "../data/action";
import store from "../data/store";
import { arrayRemove, deepCopy, isObjectValueEqual, objectUpdate, parseTimePoint } from "../utils/utils";
import RemoteLogin from "./RemoteLogin";

function AccountTag(props) {
  const { user, onRefresh, onClick } = props;
  return <ListItem button onClick={async () => { onClick && onClick(user); }}>
    <ListItemText>
      <Box>
        {user.enabled ? <><Typography variant="h5" color="primary">{`${user.username}`}</Typography></> :
          <s><Typography variant="h5" color="textSecondary">{`${user.username}`}</Typography></s>}
        {/* <Typography variant="h5" color={user.enabled ? "textPrimary" : "textSecondary"}>{`${user.username}`}</Typography> */}
      </Box>
      <Box>
        <Typography variant="body2">{`${user.enabled ? "管理已开启" : "管理已关闭"};更新于: ${parseTimePoint(user.created_at)}`}</Typography>
      </Box>
    </ListItemText>
    <ListItemSecondaryAction>
      <IconButton onClick={async () => {
        // DELETE Account
        const resp = await api.request(`account?username=${user.username}`, "DELETE");
        if (resp.code == 200)
          onRefresh && onRefresh();
      }}>
        <DeleteIcon></DeleteIcon>
      </IconButton>
    </ListItemSecondaryAction>
  </ListItem>
}

export default function Manage(props) {
  const [state, setInnerState] = React.useState({
    requestingAccounts: false,
    dialogAddAccountOpen: false,
    dialogSetAccountOpen: false,
    addMode: true,
    account: null,
  });
  const accounts = store.getState().account;
  const [ignored, forceUpdate] = React.useReducer(x => x + 1, 0);
  const setState = (update) => setInnerState(objectUpdate(state, update));

  if (!state.requestingAccounts) {
    setState({ requestingAccounts: true });
    api.request("account", "GET").then(resp => {
      if (resp.code !== 200) {
        store.dispatch(setErrorInfo(resp));
        return;
      }
      // console.log('update', resp.data.accounts);
      store.dispatch(setAccounts(resp.data.accounts));
      forceUpdate();
    });
  }
  // console.log('acconts', accounts);
  const content = state.requestingAccounts ? ((!accounts) ? <div><LinearProgress /></div> :
    <List>{accounts.map((d, i) => <AccountTag key={i} user={d} onRefresh={() => {
      setState({ requestingAccounts: false });
    }} onClick={async user => {
      setState({ account: user, dialogSetAccountOpen: true });
    }}></AccountTag>)}</List>
  ) : null;

  return <Container>
    <Grid container spacing={3}>
      <Grid item lg={8} sm={12}>
        <Typography variant="h4">被管理账号列表</Typography>
        {content}
      </Grid>
      <Grid item lg={4} sm={12}>
        <Container maxWidth="xs">
          <List>
            <ListSubheader>新被管理账号</ListSubheader>
            <ListItem>
              <Button fullWidth variant="contained" color="secondary" onClick={() => {
                setState({ dialogAddAccountOpen: true, addMode: true });
              }}>添加新被管理账号</Button>
            </ListItem>
            <ListItem>
              <Button fullWidth disabled variant="contained">设置默认被管理账号</Button>
            </ListItem>

            <ListSubheader>全部被管理账号管理</ListSubheader>
            <ListItem>
              <Button fullWidth disabled={(accounts && accounts.length === 0) || (accounts === null)} variant="outlined" onClick={async () => {
                for (const account of accounts) {
                  const resp = await api.request(`account?username=${account.username}`, "DELETE");
                }
                setState({ requestingAccounts: false });
              }}>删除全部被管理账号</Button>
            </ListItem>
          </List>
        </Container>
      </Grid>
    </Grid>
    <Dialog open={state.dialogAddAccountOpen} onClose={() => { setState({ dialogAddAccountOpen: false }); }}>
      <DialogTitle>添加新被管理账号</DialogTitle>
      <DialogContent>
        <RemoteLogin onFinish={() => {
          setState({ dialogAddAccountOpen: false, requestingAccounts: false });
          forceUpdate();
        }}></RemoteLogin>
      </DialogContent>
    </Dialog>
    <Dialog open={state.dialogSetAccountOpen} onClose={() => { setState({ dialogSetAccountOpen: false, account: null }); }}>
      <DialogTitle>是否{(state.account && state.account.enabled) ? "关闭管理" : "打开管理"}？</DialogTitle>
      <DialogActions>
        <Button color="primary" onClick={() => {
          setState({ dialogSetAccountOpen: false, account: null });
        }}>
          取消
        </Button>
        <Button color="primary" autoFocus onClick={async () => {
          const resp = await api.request(`account?username=${state.account.username}&enabled=${state.account.enabled ? 0 : 1}`, "PATCH");
          // console.log('resp:', resp);
          if (resp.code == 200) {
            setState({ dialogSetAccountOpen: false, account: null, requestingAccounts: false });
            forceUpdate();
          }
        }}>
          确定
        </Button>
      </DialogActions>
    </Dialog>
  </Container>;
}