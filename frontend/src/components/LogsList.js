import React from 'react';
import { List, ListItem, ListItemSecondaryAction, Container, Button, Select, MenuItem, LinearProgress, ListItemText, Typography } from "@material-ui/core";
import { objectUpdate, parseTimePoint } from '../utils/utils';
import { api } from '../api/api';

export default function LogsList(props) {
  // const levels = {
  //   debug: 10, info: 20, warning: 30, error: 40, critical: 50
  // };
  const levels = {
    调试: 10, 信息: 20, 警告: 30, 错误: 40, 致命错误: 50
  };
  const colors = {
    10: "textSecondary", 20: "textPrimary", 30: "primary", 40: "secondary", 50: "secondary"
  };
  const stateDefault = {
    level: levels.信息,
    limit: 30,
    offset: 0,
    requested: false,
    logs: []
  };
  const [state, setInnerState] = React.useState(stateDefault);
  const setState = (update) => setInnerState(objectUpdate(state, update));

  let content = null;
  if (!state.requested) {
    api.request(`log?limit=${state.limit}&offset=${state.offset}&level=${state.level}`, "GET").then(resp => {
      // console.log('log got', resp);
      setState({ requested: true, logs: resp.data.logs });
    });
    content = <LinearProgress></LinearProgress>;
  } else {
    if (state.logs.length == 0) {
      content = <Typography color="textSecondary">列表为空。</Typography>
    } else {
      content = <List>
        {state.logs.map((log, k) => <ListItem>
          <ListItemText color={colors[log.level]} primary={`[${k}] ` + log.text}></ListItemText>
          <ListItemSecondaryAction><Typography variant="body2" color="textSecondary">{parseTimePoint(log.created_at)}</Typography></ListItemSecondaryAction>
        </ListItem>)}
      </List>;
    }
  }

  return <Container>
    <span>设置日志查看等级<Select value={state.level} onChange={e => {
      setState({ level: e.target.value, requested: false });
    }}>
      {Object.keys(levels).map((key, i) => <MenuItem key={i} value={levels[key]}>{key}</MenuItem>)}
    </Select></span>
    <span><Button size="small" onClick={() => { setState({ requested: false }); }} color="primary">刷新</Button></span>
    <Container style={{ maxHeight: 360, overflow: "auto" }}>
      {content}
    </Container>
  </Container>;
}