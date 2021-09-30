import React from "react"
import Container from '@material-ui/core/Container';
// import ReserveTables from "../components/ReserveTables";
import { Divider, Table, TableBody, TableCell, TableRow, Typography } from "@material-ui/core";
import store from "../data/store";
import Manage from "./Manage";
import LogsList from "../components/LogsList";
import { api } from "../api/api";

class StateNow extends React.Component {
  constructor(props) {
    super(props);
    this.state = store.getState({
      requested: false,
      fetched_task: null,
      account: []
    });
    this.unsubscribe = store.subscribe(() => {
      // console.log("store update", store.getState().account);
      if (store.getState().account && store.getState().account.length > 0)
        this.setState({
          account: store.getState().account
        });
    });
  }
  componentWillUnmount() {
    this.unsubscribe();
  }
  render() {
    // console.log('launch: got account', this.state.account);
    let enabled_count = 0;
    for (const account of this.state.account) if (account.enabled) enabled_count++;
    if (!this.state.requested) {
      this.setState({ requested: true });
      api.request('state', 'GET').then(resp => {
        this.setState({ fetched_task: resp.data.state.fetched_task });
      });
    }
    return (<Table>
      <TableBody>
        <TableRow>
          <TableCell align="center">被管理账号数量</TableCell>
          <TableCell align="center">已开启管理数量</TableCell>
          <TableCell align="center">已经抢到的任务数量</TableCell>
        </TableRow>
        <TableRow>
          <TableCell align="center">{this.state.account.length}个</TableCell>
          <TableCell align="center">{enabled_count}个</TableCell>
          <TableCell align="center">{this.state.fetched_task}个</TableCell>
        </TableRow>
      </TableBody>
    </Table>);
  }
}

function Launch(props) {
  return (<Container>
    <Typography variant="h5">执行状态</Typography>
    <Divider></Divider>
    <StateNow></StateNow>
    <LogsList></LogsList>
    <br />
    <Typography variant="h5">账号管理</Typography>
    <Divider></Divider>
    <Manage></Manage>
  </Container>);
}

export default Launch;