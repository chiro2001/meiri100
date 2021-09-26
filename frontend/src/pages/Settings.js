import React from "react"
import Container from '@material-ui/core/Container';
import { Button, MenuItem, FormControl, InputLabel, List, ListItem, ListItemSecondaryAction, ListItemText, Select, ListSubheader, Switch, Dialog, DialogTitle, DialogContent, Typography, DialogActions, Box, IconButton, DialogContentText } from "@material-ui/core";
import DeleteIcon from '@material-ui/icons/Delete';
import store from "../data/store";
import { setConfig, setErrorInfo, setMessage } from "../data/action";
import { funDownload } from "../utils/utils";
import ListInfo from "../components/ListInfo";
import { api } from "../api/api";
import Config from "../Config";
import RemoteLogin from "./RemoteLogin";

function Settings(props) {
  const [themeName, setThemeName] = React.useState(store.getState().config.data.theme_name);
  const refConfigFileInput = React.useRef();
  const [resetSettingsOpen, setResetSettingsOpen] = React.useState(false);
  const [deleteDataOpen, setDeleteDataOpen] = React.useState(false);
  const [openDaemon, setOpenDaemon] = React.useState(false);
  const [openUser, setOpenUser] = React.useState(false);
  const [openResetShop, setOpenResetShop] = React.useState(false);
  const [openSelectShop, setOpenSelectShop] = React.useState(false);
  const [openNewShop, setOpenNewShop] = React.useState(false);

  const resetSettings = function () {
    let c = store.getState().config;
    c.data = c.data_default;
    c.save();
    c.load();
    store.dispatch(setConfig(c));
  }

  const user = store.getState().user;

  return (<Container maxWidth="md">
    <List>
      <ListSubheader>用户账号</ListSubheader>
      <ListItem>
        <ListItemText primary="用户名"></ListItemText>
        <ListItemSecondaryAction>
          {user.username}
        </ListItemSecondaryAction>
      </ListItem>
      <ListItem button onClick={() => { setOpenUser(true); }}>
        <ListItemText primary="详细信息"></ListItemText>
      </ListItem>
      <ListItem button>
        <ListItemText primary="修改信息"></ListItemText>
      </ListItem>
      <ListItem button onClick={() => {
        Config.clear();
        setTimeout(() => { window.location.reload(); }, 500);
      }}>
        <ListItemText primary="退出当前账号"></ListItemText>
      </ListItem>
      <ListSubheader>用户门店</ListSubheader>
      <ListItem button onClick={() => { setOpenDaemon(true); }}>
        <ListItemText primary="当前门店信息"></ListItemText>
      </ListItem>
      <ListItem button onClick={() => { setOpenResetShop(true); }}>
        <ListItemText primary="解绑当前门店"></ListItemText>
        <ListItemSecondaryAction><Typography variant="body1" color="textSecondary">{store.getState().daemon &&
          store.getState().daemon.shop_info && store.getState().daemon.shop_info.branchName}</Typography></ListItemSecondaryAction>
      </ListItem>
      <ListItem button onClick={() => { setOpenSelectShop(true); }}>
        <ListItemText primary="管理/切换当前已绑定门店"></ListItemText>
      </ListItem>
      <ListItem button onClick={() => { setOpenNewShop(true); }}>
        <ListItemText primary="绑定并且切换到新的门店"></ListItemText>
      </ListItem>
      <ListSubheader>外观</ListSubheader>
      <ListItem>
        <ListItemText primary="主题设置"></ListItemText>
        <ListItemSecondaryAction>
          <FormControl>
            {/* <InputLabel></InputLabel> */}
            <Select value={themeName} onChange={e => {
              setThemeName(e.target.value);
              let c = store.getState().config;
              c.data.theme_name = e.target.value;
              c.theme = c.theme_avaliable[c.data.theme_name];
              c.save();
              store.dispatch(setConfig(c));
              setTimeout(() => { window.location.reload(); }, 200);
            }}>
              {store.getState().config.data.theme_avaliable.map((v, k) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
            </Select>
          </FormControl>
        </ListItemSecondaryAction>
      </ListItem>
      <ListSubheader>数据管理</ListSubheader>
      <ListItem button onClick={() => {
        funDownload(store.getState().config.save(), `团购杀手配置数据(${new Date().toLocaleString()}).json`);
      }}>
        <ListItemText primary="数据导出"></ListItemText>
      </ListItem>
      <ListItem button onClick={() => {
        // console.log(refConfigFileInput)
        refConfigFileInput.current.click();
      }}>
        <ListItemText primary="数据导入"></ListItemText>
        <ListItemSecondaryAction>
          <input type="file" accept=".json" hidden name="file-gbk-data" ref={refConfigFileInput} onChange={e => {
            // console.log(e);
            let files = e.target.files;
            if (files.length === 0) {
              store.dispatch(setMessage("未选择文件"));
              return;
            }
            try {
              let file = files[0];
              let reader = new FileReader();
              reader.readAsText(file, 'UTF-8');
              reader.onload = evt => {
                const fileData = evt.target.result;
                try {
                  const js = JSON.parse(fileData);
                  if (!js.version_frontend) {
                    store.dispatch(setMessage("文件类型错误或者文件已经损坏"));
                    return;
                  }
                  if (js.version_frontend > store.getState().config.data.version_frontend) {
                    store.dispatch(setMessage(`存档文件版本(${js.version_frontend}高于当前版本${store.getState().config.data.version_frontend})，请更新到最新版`));
                    return;
                  }
                  let c = store.getState().config;
                  c.data = js;
                  store.dispatch(setConfig(c));
                  store.dispatch(setMessage("数据导入完成"));
                } catch (e) {
                  store.dispatch(setErrorInfo(e));
                }
              };
            } catch (e) {
              store.dispatch(setErrorInfo(e));
            }
          }}></input>
        </ListItemSecondaryAction>
      </ListItem>
      <ListItem>
        <ListItemText primary="设置数据同步"></ListItemText>
        <ListItemSecondaryAction>
          <Switch defaultChecked={store.getState().config.data.settings_async} onChange={e => {
            let c = store.getState().config;
            c.data.settings_async = e.target.checked;
            c.save();
            store.dispatch(setConfig(c));
          }}></Switch>
        </ListItemSecondaryAction>
      </ListItem>
      <ListItem button onClick={() => setResetSettingsOpen(true)}>
        <ListItemText primary="回到默认设置"></ListItemText>
      </ListItem>
      <ListItem button onClick={() => setDeleteDataOpen(true)}>
        <ListItemText primary="删除所有数据"></ListItemText>
      </ListItem>
    </List>
    <ListInfo data={store.getState().user} open={openUser} keyNames={{
      username: '用户名', nick: '昵称', phone: '用户手机号', profile: '详细信息', state: '用户状态', created_at: '创建于', updated_at: '更新于'
    }} title="用户信息" onClose={() => { setOpenUser(false); }}></ListInfo>
    <ListInfo data={store.getState().daemon} open={openDaemon} keyNames={{
      cookies: '远程登录凭据', shop_info: "门店详细信息", solution_id: "解决方案编号"
    }} title="门店信息" onClose={() => { setOpenDaemon(false); }}></ListInfo>
    <Dialog open={resetSettingsOpen} onClose={() => setResetSettingsOpen(false)}>
      <DialogTitle>
        回到默认设置
      </DialogTitle>
      <DialogContent>
        <Typography variant="body1">此操作将会清除所有设置数据，确认操作？</Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setResetSettingsOpen(false)}>取消</Button>
        <Button onClick={() => {
          resetSettings();
          window.location.reload();
        }}>确定</Button>
      </DialogActions>
    </Dialog>
    <Dialog open={deleteDataOpen} onClose={() => setDeleteDataOpen(false)}>
      <DialogTitle>
        删除所有数据
      </DialogTitle>
      <DialogContent>
        <Typography variant="body1">此操作将会清除软件数据，确认操作？</Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setDeleteDataOpen(false)}>取消</Button>
        <Button onClick={() => {
          resetSettings();
          window.location.reload();
        }}>确定</Button>
      </DialogActions>
    </Dialog>
    <Dialog open={openResetShop} onClose={() => { setOpenResetShop(false); }}>
      <DialogTitle>解绑当前门店</DialogTitle>
      <DialogContent>
        <Typography variant="body1">此操作将会解除门店和<b>本网站</b>的数据绑定，需要<b>重新绑定</b>才能使用网站功能。是否继续？</Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => { setOpenResetShop(false); }}>取消</Button>
        <Button onClick={async () => {
          // const resp2 = await api.request("remote_login", "GET");
          // console.log(resp2);
          const resp = await api.request("remote_login", "DELETE");
          console.log('delete cookies:', resp);
          if (resp.code !== 200) {
            store.dispatch(setErrorInfo(`删除失败: ${resp.code}, ${resp.message}, ${resp.error}`));
          } else {
            window.location.reload();
            // setOpenResetShop(false);
          }
        }} color="secondary">确定</Button>
      </DialogActions>
    </Dialog>
    <Dialog open={openSelectShop} onClose={() => { setOpenSelectShop(false); }}>
      <DialogTitle>选择一家门店</DialogTitle>
      <DialogContent>
        <List>
          <ListItem>
            <Typography variant="body2" color="textSecondary">注意，切换门店之后原有门店计划将停止执行。</Typography>
          </ListItem>
          {store.getState().daemon.shops ?
            Object.keys(store.getState().daemon.shops).map((v, k) => {
              const d = store.getState().daemon.shops[v];
              return <ListItem button key={v} onClick={async () => {
                console.log('switching to', d);
                if (!d.cookies) return;
                await api.request('remote_login', "POST", { cookies: d.cookies });
                setOpenSelectShop(false);
              }}>
                <Box style={{ display: 'flex', flexDirection: "row" }}>
                  <Box style={{ display: 'flex', flexDirection: "column" }}>
                    <Typography variant="body1">{`${d.shopName} - ${d.branchName}`}</Typography>
                    <Typography variant="body2" color="textSecondary">{`${d.shopId}`}</Typography>
                  </Box>
                </Box>
                <ListItemSecondaryAction>
                  <IconButton onClick={async () => {
                    console.log('to delete:', d);
                    await api.request("remote_login", "DELETE", { shop_id: d.shopId });
                    if (store.getState().daemon.shop_info && d.shopId === store.getState().daemon.shop_info.shopId) window.location.reload();
                  }}>
                    <DeleteIcon></DeleteIcon>
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>;
            })
            : <ListItem><ListItemText>无门店数据</ListItemText></ListItem>}
        </List>
      </DialogContent>
    </Dialog>
    <Dialog open={openNewShop} onClose={() => { setOpenNewShop(false); }}>
      <DialogContent>
        <RemoteLogin forceLogin onFinish={() => {
          console.log('onFinish');
          setTimeout(() => { window.location.reload(); }, 3000);
        }}></RemoteLogin>
      </DialogContent>
    </Dialog>
  </Container>)
}

export default Settings;