import { Select, Box, Button, Checkbox, Collapse, Container, Dialog, DialogActions, DialogContent, DialogTitle, Grid, IconButton, List, ListItem, ListItemSecondaryAction, ListItemText, ListSubheader, makeStyles, TextField, Typography, MenuItem } from "@material-ui/core";
import DeleteIcon from '@material-ui/icons/Delete';
import moment from "moment";
import React from "react";
import { api } from "../api/api";
import Actions, { wrapAction } from "../components/Actions";
import { ActionTag, updateActionData, isActionModified } from "../components/Actions";
import Triggers, { updateTriggerData, wrapTrigger } from "../components/Triggers";
import { TriggerTag, isTriggerModified } from "../components/Triggers";
import { setErrorInfo, setMessage, setTasks, updateTypes } from "../data/action";
import store from "../data/store";
import { arrayRemove, deepCopy, formatDateTime, getNewNumberString, isObjectValueEqual, objectUpdate, timedeltaUnits } from "../utils/utils";
import { ActionData } from "./ListEdit";

let taskDialogUpdate = false;

const useStyles = makeStyles((theme) => ({
  nested: {
    paddingLeft: theme.spacing(4),
  },
  centerText: {
    display: 'flex',
    alignItems: "center",
    justifyContent: "center",
    // overflow: 'hidden',
    whiteSpace: 'nowrap',
  }
}));

export function setTaskDialogUpdate(val) { taskDialogUpdate = val; }

let roomItemUpdated = false;

export default function TaskDialog(props) {
  const classes = useStyles();
  const { addMode, open, onClose, onRefresh, onSave, targets, simpleMode } = props;
  const taskOld = props.taskOld === true ? null : props.taskOld;
  console.log('targets', targets);
  const baseTaskName = (targets && targets.taskName) ? targets.taskName : '未命名任务';
  const realDefaultTask = {
    task_name: baseTaskName,
    triggers: [],
    actions: [],
  };
  const defaultTask = addMode ? (props.defaultTask ? props.defaultTask : realDefaultTask) : taskOld ? taskOld : (props.defaultTask ? props.defaultTask : realDefaultTask);
  const defaultCollapseOpen = {
    timenode: false,
    cycle: false,
    stock: false
  };
  const defaultOperations = {
    '>': '大于',
    '<': '小于',
    '==': "等于",
    '>=': '大于等于',
    '<=': "小于等于",
    '!=': '不等于'
  };
  const [state, setInnerState] = React.useState({
    dialogAddTaskOpen: false,
    dialogAddTriggerOpen: false,
    dialogAddActionOpen: false,
    dialogUpdateTrigger: false,
    task: defaultTask,
    requestingTaskData: false,
    defaultTid: null,
    useSimpleMode: simpleMode,
    collapseOpen: defaultCollapseOpen,
    simpleData: {
      timenodeTime: `datetime|${formatDateTime(new Date())}`,
      timenodePrice: 100,
      cycleTime: `timedelta|${timedeltaUnits["周"]}`,
      cyclePrice: 100,
      stockOperator: '>',
      stockPrice: 100,
      stockValue: 5
    }
  });
  const setState = (update) => setInnerState(objectUpdate(state, update));
  const setCollapseToggle = (name) => {
    // setState({ collapseOpen: objectUpdate(state.collapseOpen, { [name]: !state.collapseOpen[name] }) });
    setState({ collapseOpen: objectUpdate(defaultCollapseOpen, { [name]: !state.collapseOpen[name] }) });
  }
  // console.log('baseTaskName', baseTaskName, 'defaultTask', defaultTask);
  // console.log('state', state);
  const [ignored, forceUpdate] = React.useReducer(x => x + 1, 0);
  const taskData = store.getState().types.task_data;
  if (!roomItemUpdated && targets && targets.roomItem) {
    roomItemUpdated = true;
    try {
      setState({
        simpleData: objectUpdate(state.simpleData, {
          timenodePrice: targets && targets.roomItem ? targets.roomItem.price : state.simpleData.timenodePrice,
          cyclePrice: targets && targets.roomItem ? targets.roomItem.price : state.simpleData.cyclePrice
        })
      });
    } catch (e) {
      roomItemUpdated = false;
      console.error(e);
    }
  }

  // console.log('taskNow', state.task);
  if (!addMode && (taskDialogUpdate || (isObjectValueEqual(state.task, realDefaultTask) && !isObjectValueEqual(defaultTask, realDefaultTask)))) {
    taskDialogUpdate = false;
    setState({ task: defaultTask });
  } else if (taskDialogUpdate) {
    taskDialogUpdate = false;
    setState({ task: defaultTask });
  }

  if (!state.requestingTaskData && !taskData) {
    setState({ requestingTaskData: true });
    api.request("task", 'PATCH').then(resp => {
      // console.log("resp", resp);
      let taskData = resp.data.task_data;
      taskData.tid = null;
      store.dispatch(updateTypes("task_data", taskData));
      forceUpdate();
    })
  }

  const handleAddTask = addMode ? () => {
    // console.log('pass#2');
    if (!taskData) {
      setErrorInfo("Task数据为空。");
      console.error("Task数据为空。");
      return;
    }
    // const task = objectUpdate(taskData, { triggers: state.task.triggers, actions: state.task.actions, task_name: state.task.task_name, tid: null, });
    const task = objectUpdate(taskData, state.task);
    console.log('task', task);
    return api.request('task', "POST", { task }).then(resp => {
      // console.log('resp', resp);
      if (resp.code !== 200) return;
      const defaultTid = resp.data.tid ? (resp.data.tid + 1) : null;
      setState({
        defaultTid,
        taskName: store.getState().types.task_data ? `${baseTaskName}${defaultTid ? defaultTid : ""}` : baseTaskName,
      });
      onRefresh && onRefresh();
    });
  } : () => {
    if (!taskOld) return;
    const task = objectUpdate(taskOld, state.task);
    console.log('task', task);
    if (onSave)
      return onSave(task);
    else return new Promise((resolve, reject) => { resolve(); });
  };

  const dialogContent = state.useSimpleMode ?
    <List>
      {simpleMode ? <ListItem>
        <Button variant="outlined" onClick={() => { setState({ useSimpleMode: !state.useSimpleMode }); }} fullWidth color="secondary">高级模式</Button>
      </ListItem> : null}
      <ListItem>
        <ListItemText primary="计划名称"></ListItemText>
        <ListItemSecondaryAction>
          <TextField value={state.task.task_name} onChange={e => {
            let newTask = deepCopy(state.task);
            newTask.task_name = e.target.value;
            setState({ task: newTask });
          }}></TextField>
        </ListItemSecondaryAction>
      </ListItem>
      <ListItem button onClick={() => {
        setCollapseToggle('timenode');
      }}>
        <Box style={{ display: "flex", flexFlow: "row" }}>
          <Checkbox checked={state.collapseOpen.timenode}></Checkbox>
          <Box>
            <Box className={classes.centerText} style={{ height: "100%" }}>在某一个时间点改变价格</Box>
          </Box>
        </Box>
      </ListItem>
      <Collapse in={state.collapseOpen.timenode} timeout="auto" unmountOnExit className={classes.nested}>
        <Box style={{ display: "flex", flexFlow: "row", justifyContent: "space-between" }}>
          <Box className={classes.centerText}>在</Box>
          <ActionData value={state.simpleData.timenodeTime} onChange={e => {
            if (!e) setState({ simpleData: objectUpdate(state.simpleData, { timenodeTime: `datetime|${formatDateTime(new Date())}` }) });
            else setState({ simpleData: objectUpdate(state.simpleData, { timenodeTime: `datetime|${formatDateTime(e)}` }) });
          }} onDelete={() => { setState({ simpleData: objectUpdate(state.simpleData, { timenodeTime: "datetime|" }) }); }}></ActionData>
          <Box className={classes.centerText}>调整价格到</Box>
          <TextField style={{ maxWidth: 60 }} inputProps={{ style: { textAlign: "center" } }} value={`${state.simpleData.timenodePrice}`} onChange={e => {
            const newValue = getNewNumberString(e.target.value);
            if (newValue === null) return;
            setState({ simpleData: objectUpdate(state.simpleData, { timenodePrice: newValue }) });
          }}></TextField>
        </Box>
      </Collapse>
      <ListItem button onClick={() => {
        // setState({ collapseOpen: objectUpdate(state.collapseOpen, { cycle: !(!!state.collapseOpen.cycle) }) });
        setCollapseToggle('cycle');
      }}>
        <Box style={{ display: "flex", flexFlow: "row" }}>
          <Checkbox checked={state.collapseOpen.cycle}></Checkbox>
          <Box>
            <Box className={classes.centerText} style={{ height: "100%" }}>周期性改变价格</Box>
          </Box>
        </Box>
      </ListItem>
      <Collapse in={state.collapseOpen.cycle} timeout="auto" unmountOnExit className={classes.nested}>
        <Box style={{ display: "flex", flexFlow: "row", justifyContent: "space-between" }}>
          <Box className={classes.centerText}>每隔</Box>
          <TextField style={{ maxWidth: 60 }} inputProps={{ style: { textAlign: "center" } }} value={`${parseFloat(state.simpleData.cycleTime.slice('timedelta|'.length)) / timedeltaUnits['天']}`} onChange={e => {
            const value = parseFloat(e.target.value);
            console.log(value);
            const newValue = getNewNumberString(`${value}`);
            if (newValue === null) return;
            setState({ simpleData: objectUpdate(state.simpleData, { cycleTime: `timedelta|${newValue * timedeltaUnits['天']}` }) });
          }}></TextField>
          <Box className={classes.centerText}>天，调整价格到</Box>
          <TextField style={{ maxWidth: 60 }} inputProps={{ style: { textAlign: "center" } }} value={`${state.simpleData.cyclePrice}`} onChange={e => {
            const newValue = getNewNumberString(e.target.value);
            if (newValue === null) return;
            setState({ simpleData: objectUpdate(state.simpleData, { cyclePrice: newValue }) });
          }}></TextField>
        </Box>
      </Collapse>
      <ListItem button onClick={() => {
        setCollapseToggle('stock');
      }}>
        <Box style={{ display: "flex", flexFlow: "row" }}>
          <Checkbox checked={state.collapseOpen.stock}></Checkbox>
          <Box>
            <Box className={classes.centerText} style={{ height: "100%" }}>根据库存改变价格</Box>
          </Box>
        </Box>
      </ListItem>
      <Collapse in={state.collapseOpen.stock} timeout="auto" unmountOnExit className={classes.nested}>
        <Box style={{ display: "flex", flexFlow: "row", justifyContent: "space-between" }}>
          <Box className={classes.centerText}>在(设定值)</Box>
          <TextField style={{ maxWidth: 60 }} inputProps={{ style: { textAlign: "center" } }} value={`${state.simpleData.stockValue}`} onChange={e => {
            const newValue = getNewNumberString(e.target.value);
            if (newValue === null) return;
            setState({ simpleData: objectUpdate(state.simpleData, { stockValue: newValue }) });
          }}></TextField>
          <Select value={state.simpleData.stockOperator} onChange={e => {
            setState({ simpleData: objectUpdate(state.simpleData, { stockOperator: e.target.value }) });
          }}>
            {Object.keys(defaultOperations).map(key => <MenuItem key={key} value={key}>{defaultOperations[key]}</MenuItem>)}
          </Select>
          <Box className={classes.centerText}>库存值的时候</Box>
          <Box className={classes.centerText}>调整价格到</Box>
          <TextField style={{ maxWidth: 60 }} inputProps={{ style: { textAlign: "center" } }} value={`${state.simpleData.stockPrice}`} onChange={e => {
            const newValue = getNewNumberString(e.target.value);
            if (newValue === null) return;
            setState({ simpleData: objectUpdate(state.simpleData, { stockPrice: newValue }) });
          }}></TextField>
        </Box>
      </Collapse>
    </List> :
    <List>
      {simpleMode ? <ListItem>
        <Button variant="outlined" onClick={() => { setState({ useSimpleMode: !state.useSimpleMode }); }} fullWidth color="secondary">简单模式</Button>
      </ListItem> : null}
      <ListSubheader>计划名称</ListSubheader>
      <ListItem>
        <TextField fullWidth value={state.task.task_name} onChange={e => {
          let newTask = deepCopy(state.task);
          newTask.task_name = e.target.value;
          setState({ task: newTask });
        }}></TextField>
      </ListItem>
      <ListSubheader>触发器列表</ListSubheader>
      {state.task.triggers.map((trigger, k) => <ListItem key={trigger}>
        <TriggerTag fullWidth trigger={trigger} onSave={data => {
          console.log('saveing', data);
          let newTask = deepCopy(state.task);
          newTask.triggers[k] = data;
          setState({ task: newTask });
        }}></TriggerTag>
        <ListItemSecondaryAction>
          <IconButton onClick={() => {
            let newTask = deepCopy(state.task);
            newTask.triggers.splice(k, 1);
            setState({ task: newTask });
          }}>
            <DeleteIcon></DeleteIcon>
          </IconButton>
        </ListItemSecondaryAction>
      </ListItem>)}
      <ListSubheader>Actions列表</ListSubheader>
      {state.task.actions.map((action, k) => <ListItem key={action}>
        <ActionTag fullWidth action={action} onSave={data => {
          console.log('saveing', data);
          let newTask = deepCopy(state.task);
          newTask.actions[k] = data;
          setState({ task: newTask });
        }}></ActionTag>
        <ListItemSecondaryAction>
          <IconButton onClick={() => {
            let newTask = deepCopy(state.task);
            newTask.actions.splice(k, 1);
            setState({ task: newTask });
          }}>
            <DeleteIcon></DeleteIcon>
          </IconButton>
        </ListItemSecondaryAction>
      </ListItem>)}
      <ListItem>
        <Grid container spacing={5}>
          <Grid item xs={12} lg={6}>
            <Button fullWidth onClick={() => { setState({ dialogAddTriggerOpen: true }) }} color="primary" variant="outlined">添加触发器</Button>
          </Grid>
          <Grid item xs={12} lg={6}>
            <Button fullWidth onClick={() => { setState({ dialogAddActionOpen: true }) }} color="primary" variant="outlined">添加Action</Button>
          </Grid>
        </Grid>
      </ListItem>
    </List>;

  return <Dialog fullWidth open={open} onClose={() => { onClose && onClose(false) }}>
    <DialogTitle>{addMode ? "添加新任务" : "设置任务"}</DialogTitle>
    <DialogContent>
      {dialogContent}
      <Dialog open={state.dialogAddTriggerOpen} onClose={() => setState({ dialogAddTriggerOpen: false })}>
        <DialogTitle>选择一个触发器</DialogTitle>
        <DialogContent>
          <Triggers targets={targets} onClick={trigger => {
            console.log("trigger", trigger);
            let newTask = deepCopy(state.task);
            newTask.triggers.push(trigger);
            setState({ dialogAddTriggerOpen: false, task: newTask });
          }} selectMode></Triggers>
        </DialogContent>
      </Dialog>
      <Dialog open={state.dialogAddActionOpen} onClose={() => setState({ dialogAddActionOpen: false })}>
        <DialogTitle>选择一个Action</DialogTitle>
        <DialogContent>
          <Actions targets={targets} onClick={action => {
            console.log("action", action);
            let newTask = deepCopy(state.task);
            newTask.actions.push(action);
            setState({ dialogAddActionOpen: false, task: newTask });
          }} selectMode></Actions>
        </DialogContent>
      </Dialog>
    </DialogContent>
    <DialogActions>
      <Button color="primary" disabled={state.useSimpleMode ? (
        (() => {
          for (const col in state.collapseOpen) {
            if (state.collapseOpen[col]) return false;
          }
          return true;
        })()
      ) : (state.task.triggers.length === 0 || state.task.actions.length === 0)} onClick={async () => {
        if (!state.useSimpleMode) {
          handleAddTask().then(() => {
            setState({ task: defaultTask });
            onClose && onClose(true);
          });
        } else {
          if (!targets || (targets && !targets.roomItem)) {
            console.warn('targets error');
          }
          // 生成对应的触发器和Actions
          let triggers = [], actions = [];
          // console.log(store.getState().types);
          const defaultData = {
            triggers: store.getState().types.triggers ?
              store.getState().types.triggers :
              await ((() => {
                return new Promise((resolve, reject) => {
                  updateTriggerData((d) => { resolve(d); });
                })
              })()),
            actions: store.getState().types.actions ?
              store.getState().types.actions :
              await ((() => {
                return new Promise((resolve, reject) => {
                  updateActionData((d) => { resolve(d); });
                })
              })()),
          }
          for (const col in state.collapseOpen) {
            if (state.collapseOpen[col]) {
              if (col === 'timenode') {
                // console.log(defaultData);
                if (state.simpleData.timenodeTime === 'datetime|') {
                  store.dispatch(setMessage("时间点未设置"));
                  return;
                }
                triggers.push(objectUpdate(defaultData.triggers.date,
                  { data: objectUpdate(defaultData.triggers.date.data, { run_date: state.simpleData.timenodeTime }) }));
                actions.push(objectUpdate(defaultData.actions.adjust_price,
                  {
                    data: objectUpdate(defaultData.actions.adjust_price.data,
                      { target_price: state.simpleData.timenodePrice, item_id: targets.roomItem.itemId })
                  }));
              } else if (col === 'cycle') {
                triggers.push(objectUpdate(defaultData.triggers.interval,
                  { data: objectUpdate(defaultData.triggers.interval.data, { interval: state.simpleData.cycleTime }) }));
                actions.push(objectUpdate(defaultData.actions.adjust_price,
                  {
                    data: objectUpdate(defaultData.actions.adjust_price.data,
                      { target_price: state.simpleData.timenodePrice, item_id: targets.roomItem.itemId })
                  }));
              } else if (col === 'stock') {
                triggers.push(objectUpdate(defaultData.triggers.stock,
                  { data: objectUpdate(defaultData.triggers.stock.data, { value: state.simpleData.stockValue, operator: state.simpleData.stockOperator }) }));
                actions.push(objectUpdate(defaultData.actions.adjust_price,
                  {
                    data: objectUpdate(defaultData.actions.adjust_price.data,
                      { target_price: state.simpleData.timenodePrice, item_id: targets.roomItem.itemId })
                  }));
              }
            }
          }
          if (triggers.length === 0 || actions.length === 0) {
            console.warn("Must select actions / triggers");
            return;
          }
          const newTask = objectUpdate(state.task, { triggers, actions });
          // console.log(newTask);
          await api.request('task', "POST", { task: newTask });
          onClose && onClose(true);
        }
      }}>确定</Button>
      <Button onClick={() => { onClose && onClose(false); }}>取消</Button>
    </DialogActions>
  </Dialog >;
}