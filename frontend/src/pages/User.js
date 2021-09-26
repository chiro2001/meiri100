import { Box, Button, Container, Divider, TextField, Typography, Zoom, Fade, Avatar, List } from '@material-ui/core';
import React from 'react';
import { api } from '../api/api';
import { setMessage, setUser } from '../data/action';
import { makeStyles } from "@material-ui/core/styles";
import store from '../data/store';
import {
  HashRouter as Router,
  // BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";
import { isChinese, objectUpdate } from '../utils/utils';
import ListItemLink from '../components/ListItemLink';

const useStyles = makeStyles((theme) => ({
  small: {
    width: theme.spacing(3),
    height: theme.spacing(3),
  },
  large: {
    width: theme.spacing(7),
    height: theme.spacing(7),
  },
}));

export default function User(props) {
  const { onClose } = props;
  const classes = useStyles();
  const user = store.getState().user;
  const nick = user.nick ? user.nick : user.username;
  const nickHead = isChinese(nick[0]) ? null : `${nick}`.slice(0, 2);
  return <Container maxWidth="sm">
    <Box style={{ display: 'flex', flexDirection: "row", minWidth: 90 }}>
      <Box style={{ margin: 15 }}>
        <Avatar alt={nick} className={classes.large}>{nickHead ? nickHead : nick[0]}</Avatar>
      </Box>
      <Box style={{ margin: 8 }}>
        <Typography variant="h4">{nick}</Typography>
        {user.username ? <Typography variant="body1">@{user.username}</Typography> : null}
      </Box>
      <Box style={{ margin: 10 }}>
        <Typography variant="h5">{`${store.getState().daemon.shop_info.shopName}`}</Typography>
        <Typography variant="body1" color="textSecondary">{`${store.getState().daemon.shop_info.branchName}`}</Typography>
      </Box>
    </Box>
    {/* <Button fullWidth color="primary">跳转到设置</Button> */}
    <Router>
      <List>
        <ListItemLink to="/settings" primary="跳转到设置" onClick={() => { onClose && onClose(); }} />
      </List>
    </Router>
  </Container>;
}