import React from "react"
import Container from '@material-ui/core/Container';
// import ReserveTables from "../components/ReserveTables";
import { Divider, Table, TableBody, TableCell, TableRow, Typography } from "@material-ui/core";
import store from "../data/store";
import Manage from "./Manage";
import LogsList from "../components/LogsList";

class StateNow extends React.Component {
  constructor(props) {
    super(props);
    this.state = store.getState();
    this.unsubscribe = store.subscribe(() => {
      this.setState({
        // timetableNodes: store.getState().timetableNodes,
        // timetablePeriods: store.getState().timetablePeriods,
        // roomStockPlans: store.getState().roomStockPlans
      });
    });
  }
  componentWillUnmount() {
    this.unsubscribe();
  }
  render() {
    const accounts = store.getState().account;
    let enabled_count = 0;
    for (const account of accounts) if (account.enabled) enabled_count++;
    return (<Table>
      <TableBody>
        <TableRow>
          <TableCell align="center">被管理账号数量</TableCell>
          <TableCell align="center">已开启管理数量</TableCell>
          <TableCell align="center">LABLE2</TableCell>
        </TableRow>
        <TableRow>
          <TableCell align="center">{store.getState().account.length}个</TableCell>
          <TableCell align="center">{enabled_count}个</TableCell>
          <TableCell align="center">VALUE2</TableCell>
        </TableRow>
      </TableBody>
    </Table>);
  }
}

function Launch() {
  return (<Container>
    <Typography variant="h5">执行状态</Typography>
    <Divider></Divider>
    <StateNow></StateNow>
    <LogsList></LogsList>
    <br />
    <Typography variant="h5">数据总览</Typography>
    <Divider></Divider>
    {/* <ReserveTables /> */}
    <br />
    <Typography variant="h5">账号管理</Typography>
    <Divider></Divider>
    <Manage></Manage>
  </Container>);
}

export default Launch;