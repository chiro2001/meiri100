import React from 'react';
import { Box, Container, LinearProgress, Button, Dialog, Link, List, ListItemText, DialogTitle, DialogContent, ListItem, Typography, DialogActions } from '@material-ui/core';
import CircularProgress from '@material-ui/core/CircularProgress';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import { api } from '../api/api';
import store from '../data/store';
import { setDaemon, setErrorInfo, setTasks } from '../data/action';
import TaskDialog, { setTaskDialogUpdate } from "./TaskDialog";
import { deepCopy, weekDayList } from '../utils/utils';
import { getTargetTasks, TaskList } from '../pages/Tasks';

const useStyles = makeStyles({
  table: {
    minWidth: 1500,
  },
  foodDesc: {
    overflow: 'hidden',
    whiteSpace: 'nowrap',
    contentOverflow: 'ellipsis',
    maxWidth: 160
  },
  planButton: {
    overflow: 'hidden',
    whiteSpace: 'nowrap',
    contentOverflow: 'ellipsis',
    maxWidth: 160
  }
});

function MyTableCell(props) {
  let styles = Object.assign((props.style ? props.style : {}), { padding: 3 });
  // console.log('props.noBorder', props.noBorder);
  if (props.noBorder) styles.borderBottom = "0";
  // return <TableCell align={props.align} colSpan={props.colSpan} style={styles}>{props.content}</TableCell>
  return <TableCell align={props.align} colSpan={props.colSpan} style={styles}>{props.children}</TableCell>
}

// 容易subscribe到已经卸载的component上面...
// store.subscribe(() => {
//   console.log('(tables) redux update to', store.getState());
// });

let requestedDayData = null;
// let roomItemNow = {};
let setUpdateTimer = null;

function ReserveTable(props) {
  const classes = useStyles();
  // console.log('daemon', store.getState().daemon);
  const [requestingDaemon, setRequestingDaemon] = React.useState(false);
  const [requestingUpdate, setRequestingUpdate] = React.useState(false);
  const [ignored, forceUpdate] = React.useReducer(x => x + 1, 0);
  const { day, data } = props;
  const date = new Date().setDay(day).toDateString();
  // const [dayData, setDayData] = React.useState(data ? data : store.getState().daemon.reserve_table[date]);
  const [dayData, setDayData] = React.useState(data);
  const [roomList, setRoomList] = React.useState((store.getState().daemon &&
    store.getState().daemon.reserve_table &&
    store.getState().daemon.reserve_table[date]) ? store.getState().daemon.reserve_table[date].roomList : []);
  const [dialogAddTaskOpen, setDialogAddTaskOpen] = React.useState(null);
  const [dialogTasksListOpen, setDialogTasksListOpen] = React.useState(null);
  const [roomItemNow, setRoomItemNow] = React.useState({});
  const [requestingTasks, setRequestingTasks] = React.useState(false);

  if (!requestingTasks && (!store.getState().tasks || (store.getState().tasks || store.getState().tasks.length === 0))) {
    setRequestingTasks(true);
    api.request("task", "GET").then(resp => {
      if (resp.code !== 200) return;
      store.dispatch(setTasks(resp.data.tasks));
      forceUpdate();
    });
  }

  if (!store.getState().daemon) {
    if (!requestingDaemon) {
      setRequestingDaemon(true);
      api.request("daemon", "GET").then(resp => {
        if (resp.code !== 200) return;
        store.dispatch(setDaemon(resp.data));
      });
    }
    return <LinearProgress></LinearProgress>;
  }
  if (!store.getState().daemon.reserve_table) {
    if (!requestingUpdate) {
      setRequestingUpdate(true);
      api.request("daemon", "POST", { daemon_args: { update_all: true } }).then(resp => {
        if (resp.code !== 200) return;
        store.dispatch(setDaemon(resp.data));
      });
    }
    return <LinearProgress></LinearProgress>;
  }

  requestedDayData = JSON.stringify(store.getState().daemon.reserve_table[date]) !== '{}' && JSON.stringify(store.getState().daemon.reserve_table[date]) !== undefined;
  // console.log('requested', requestedDayData);
  // console.log('date', date);

  const PeriodTable = function (props) {
    const classes = useStyles();
    const { data, roomList } = props;
    // console.log("data", data);
    let table = {};
    let periodIds = [];
    let periodMap = {};
    for (const period of data.periodList) {
      table[period.periodId] = {};
      periodMap[period.periodId] = period;
      periodIds.push({ id: period.periodId, desc: period.periodDesc });
      for (const room of roomList) {
        table[period.periodId][room.roomName] = [];
      }
      for (const roomMapItemName in period.roomMapItemEntry) {
        if (!table[period.periodId][roomMapItemName]) table[period.periodId][roomMapItemName] = [];
        for (const roomItem of period.roomMapItemEntry[roomMapItemName]) {
          table[period.periodId][roomMapItemName].push(roomItem);
        }
      }
    }
    // console.log('table', table);
    let rows = [];
    let maxRows = {};
    // let key = 1;
    for (const periodData of periodIds) {
      const periodId = periodData.id;
      if (!table[periodId]) continue;
      let index = 0;
      while (true) {
        let notEmpty = false;
        for (const room of roomList) {
          if (!table[periodId][room.roomName] || !(table[periodId][room.roomName] && table[periodId][room.roomName][index])) {
            continue;
          }
          notEmpty = true;
        }
        if (!notEmpty) break;
        index++;
      }
      maxRows[periodId] = index;
    }
    const getCenterTable = (index, maxIndex, content, key) => {
      return index == (parseInt(maxIndex / 2)) ? (maxIndex % 2 === 1 ? (index === maxIndex - 1 ? <MyTableCell key={key} align="center" colSpan={1}>{content}</MyTableCell> :
        <MyTableCell key={key} align="center" noBorder colSpan={1}>{content}</MyTableCell>) :
        (index === maxIndex - 1 ? <MyTableCell key={key} align="center" colSpan={1}><Box style={{ position: "relative", top: -15 }}>{content}</Box></MyTableCell> :
          <MyTableCell key={key} align="center" noBorder colSpan={1}><Box style={{ position: "relative", top: -15 }}>{content}</Box></MyTableCell>)) :
        (index === maxIndex - 1 ? <MyTableCell key={key} align="center" colSpan={1}></MyTableCell> :
          <MyTableCell key={key} align="center" colSpan={1} noBorder></MyTableCell>);
    };
    for (const periodData of periodIds) {
      const periodId = periodData.id;
      if (!table[periodId]) continue;
      let index = 0;
      while (true) {
        let notEmpty = false;
        const maxIndex = maxRows[periodId] ? maxRows[periodId] : 1;
        // let row = [getCenterTable(index, maxIndex, periodData.id, key++),];
        let row = [getCenterTable(index, maxIndex, <Box component="div" className={classes.foodDesc}>
          {periodData.desc}
        </Box>, periodId),];
        for (const room of roomList) {
          if (!table[periodId][room.roomName] || !(table[periodId][room.roomName] && table[periodId][room.roomName][index])) {
            for (const i of [0, 1, 2, 3]) {
              row.push(<MyTableCell key={`${periodId}${room.roomName}${index}-blank-${i}`} colSpan={1}></MyTableCell>);
            }
            continue;
          }
          notEmpty = true;
          const roomItem = table[periodId][room.roomName][index];
          // console.log("roomItem", roomItem);
          // 价格
          row.push(<MyTableCell key={`${periodId}${room.roomName}${index}-price`} align="center" colSpan={1}>{'￥' + roomItem.price}</MyTableCell>);
          // 说明
          row.push(<MyTableCell key={`${periodId}${room.roomName}${index}-foodDesc`} align="center" colSpan={1}>
            <Box component="div" className={classes.foodDesc}>
              {roomItem.foodDesc}
            </Box>
          </MyTableCell>);
          // 库存
          row.push(getCenterTable(index, table[periodId][room.roomName] ? table[periodId][room.roomName].length : maxIndex, `${roomItem.stock}间`, `${periodId}${room.roomName}${index}-stock`));
          // 计划
          // row.push(<MyTableCell key={key} align="center" colSpan={1}><Link className={classes.planButton}>计划</Link></MyTableCell>);
          row.push(<MyTableCell key={`${periodId}${room.roomName}${index}-plan`} align="center" colSpan={1}>{
            (() => {
              let planCount = getTargetTasks({ roomItem }).length;
              return (<Link onClick={planCount === 0 ? () => {
                let parent = periodMap[periodId];
                parent.date = date;
                parent.day = day;
                console.log('day', day, 'date', date);
                let roomItemTmp = deepCopy(roomItem);
                roomItemTmp.parent = parent;
                setRoomItemNow(roomItemTmp);
                setTaskDialogUpdate(true);
                setDialogAddTaskOpen(true);
              } : () => {
                const tasks = getTargetTasks({ roomItem });
                console.log('got tasks', tasks);
                const parent = periodMap[periodId];
                parent.date = date;
                parent.day = day;
                console.log('- day', day, 'date', date);
                let roomItemTmp = deepCopy(roomItem);
                roomItemTmp.parent = parent;
                setRoomItemNow(roomItemTmp);
                setDialogTasksListOpen(tasks);
              }} className={classes.planButton}>计划{planCount > 0 ? (`(${planCount})`) : ''}</Link>);
            })()
          }</MyTableCell>);
        }
        if (!notEmpty) break;
        rows.push(row);
        index++;
      }
    }
    return rows.map((v, k) => <TableRow style={{ height: 30 }} key={k}>{v}</TableRow>);
  };

  if (!setUpdateTimer) {
    setUpdateTimer = true;
    // 每分钟更新数据
    setTimeout(() => {
      if (!updateData) return;
      updateData();
    }, 60 * 1000);
  }

  const updateData = () => {
    // console.log('updating daemon!');
    if (!requestedDayData) {
      requestedDayData = true;
      api.request("daemon", "POST", { daemon_args: { reserve_table: { date } } }).then(resp => {
        if (resp.code !== 200) return;
        store.dispatch(setDaemon(resp.data));
        requestedDayData = false;
        forceUpdate();
      });
    } else {
      let reserveTableData = store.getState().daemon.reserve_table[date];
      // console.log('got from redux:', reserveTableData);
      if (reserveTableData) {
        setDayData(reserveTableData);
        setRoomList(reserveTableData.roomList);
        // 也是要请求一遍的
        api.request("daemon", "POST", { daemon_args: { reserve_table: { date } } }).then(resp => {
          if (resp.code !== 200) return;
          store.dispatch(setDaemon(resp.data));
          requestedDayData = false;
          forceUpdate();
        });
      } else {
        // console.warn('got empty reserveTableData', dayData, store.getState().daemon.reserve_table, date, JSON.stringify(store.getState().daemon.reserve_table[date]));
      }
    }
  };

  const updateTaskData = () => {
    // 更新Task数据
    updateData();
    api.request("task", "GET").then(resp => {
      if (resp.code !== 200) return;
      store.dispatch(setTasks(resp.data.tasks));
      setDialogTasksListOpen(null);
      forceUpdate();
    });
  };

  if (!dayData) {
    updateData();
    return (<Container>
      <LinearProgress></LinearProgress>
    </Container>);
  }
  let tableHeaderCells = [<TableCell key="time" align="center" colSpan={1}>时间</TableCell>,];
  roomList.map((d, i) => {
    tableHeaderCells.push(<TableCell key={'a' + d + i} align="center" colSpan={2}>售卖内容</TableCell>);
    tableHeaderCells.push(<TableCell key={'b' + d + i} align="center" colSpan={1}>库存</TableCell>);
    tableHeaderCells.push(<TableCell key={'c' + d + i} align="center" colSpan={1}>计划</TableCell>);
    // tableHeaderCells.push(<TableCell key={'d' + d + i} align="center" colSpan={1}>临时下线</TableCell>);
  });
  const tableHeader = <TableHead>
    <TableRow>
      <TableCell align="center" colSpan={1}>[{date.slice(date.length - 2, date.length)}日{'周' + ["日", '一', '二', '三', '四', '五', '六'][day]}]</TableCell>
      {roomList.map((d, i) =>
        <TableCell align="center" key={i} colSpan={4}>{d.roomName}({d.roomCapacity})</TableCell>
      )}
    </TableRow>
    <TableRow>
      {tableHeaderCells}
    </TableRow>
  </TableHead>;
  if (!dayData || !dayData.periodList) {
    // console.log('no data!', dayData, typeof (dayData));
    return (<Container>
      <header></header>
      <LinearProgress></LinearProgress>
    </Container>);
  }
  // console.log("roomItemNow", roomItemNow);
  return (
    <Container>
      <TableContainer component={Paper}>
        <Table stickyHeader className={classes.table}>
          {tableHeader}
          <TableBody>
            {/* {dayData.periodList.map((d, i) =>
              <Period key={'period' + i} data={d} roomList={roomList}></Period>
            )} */}
            <PeriodTable data={dayData} roomList={roomList}></PeriodTable>
          </TableBody>
        </Table>
      </TableContainer>
      <Dialog open={!!dialogTasksListOpen} onClose={() => { setDialogTasksListOpen(null); }}>
        <DialogTitle>任务列表</DialogTitle>
        <DialogContent>
          {/* {roomItemNow && JSON.stringify(roomItemNow) !== "{}" ?  */}
          {dialogTasksListOpen ? <TaskList fullWidth tasks={dialogTasksListOpen}
            // onClick={task => {
            //   console.log('click task', task);
            //   setDialogAddTaskOpen(task);
            // }}
            onUpdate={() => {
              api.request("task", "GET").then(resp => {
                if (resp.code !== 200) return;
                store.dispatch(setTasks(resp.data.tasks));
                forceUpdate();
              });
            }}></TaskList> : null
            // <code>{`${console.log(roomItemNow, dialogTasksListOpen)}`}</code>
          }
        </DialogContent>
        <DialogActions>
          <Button color="primary" onClick={() => {
            setTaskDialogUpdate(true);
            setDialogAddTaskOpen(true);
          }}>添加任务</Button>
          <Button color="primary" onClick={() => { setDialogTasksListOpen(null); }}>取消</Button>
        </DialogActions>
      </Dialog>
      <TaskDialog
        simpleMode
        taskOld={dialogAddTaskOpen}
        addMode={dialogAddTaskOpen === true}
        targets={{ roomItem: roomItemNow, taskName: (roomItemNow && JSON.stringify(roomItemNow) !== "{}") ? `${roomItemNow.roomType}周${weekDayList[new Date().getDay()]}${roomItemNow.parent.periodDesc}` : null }}
        open={!!dialogAddTaskOpen && (roomItemNow && JSON.stringify(roomItemNow) !== '{}')}
        onRefresh={() => {
          updateTaskData();
        }}
        onClose={(isOk) => {
          setDialogAddTaskOpen(null);
          if (isOk) updateTaskData();
        }}
        onSave={task => {
          console.log("post task", task);
          return api.request_key('task', task.tid, "POST", { task }).then(resp => {
            // setState({ requestingTasks: false });
            console.log("update task done");
          });
        }}
      ></TaskDialog>
    </Container>
  );
}

export default ReserveTable;