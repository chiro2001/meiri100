import React from "react"
import Container from '@material-ui/core/Container';
import ReserveTables from "../components/ReserveTables";
import { Divider, Table, TableBody, TableCell, TableRow, Typography } from "@material-ui/core";
import store from "../data/store";

class StateNow extends React.Component {
  constructor(props) {
    super(props);
    this.state = store.getState();
    this.unsubscribe = store.subscribe(() => {
      this.setState({
        timetableNodes: store.getState().timetableNodes,
        timetablePeriods: store.getState().timetablePeriods,
        roomStockPlans: store.getState().roomStockPlans
      });
    });
  }
  componentWillUnmount() {
    this.unsubscribe();
  }
  render() {
    return (<Table>
      <TableBody>
        <TableRow>
          <TableCell align="center">任务数量</TableCell>
          <TableCell align="center">LABLE1</TableCell>
          <TableCell align="center">LABLE2</TableCell>
        </TableRow>
        <TableRow>
          <TableCell align="center">{store.getState().tasks.length}个</TableCell>
          <TableCell align="center">VALUE1</TableCell>
          <TableCell align="center">VALUE2</TableCell>
        </TableRow>
      </TableBody>
    </Table>);
  }
}

function Launch() {
  return (<Container style={{ overflowX: 'auto', width: '100%' }}>
    <Typography variant="h5">执行状态</Typography>
    <StateNow></StateNow>
    <br />
    <Typography variant="h5">数据总览</Typography>
    <ReserveTables />
  </Container>);
}

export default Launch;