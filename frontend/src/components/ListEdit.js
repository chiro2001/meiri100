import { Select, Box, Button, Container, Dialog, DialogActions, DialogContent, DialogTitle, List, ListItem, ListItemSecondaryAction, ListItemText, TextField, Typography, MenuItem, IconButton } from "@material-ui/core";
import { DateTimePicker } from "@material-ui/pickers";
import React from "react";
import DeleteIcon from '@material-ui/icons/Delete';
import store from "../data/store";
import { formatDateTime, getNewNumberString, isIterator, objectUpdate, timedeltaUnits } from "../utils/utils";
import moment from "moment";

export function ActionData(props) {
  const { value, onChange, onDelete } = props;
  return <Box>
    {value === null || value === undefined || value === 'datetime|' ?
      <Button color="secondary" onClick={() => { onChange && onChange(null); }}>点击设置</Button> :
      <Box style={{ display: "flex", flexDirection: "row" }}>
        <DateTimePicker
          value={value.slice("datetime|".length)}
          onChange={onChange}
        ></DateTimePicker>
        <IconButton onClick={onDelete}>
          <DeleteIcon></DeleteIcon>
        </IconButton>
      </Box>}
  </Box>;
}

export default function ListEdit(props) {
  const { defaultValue, open, onClose, title, keyNames, dataType, typeName } = props;
  const dismiss = props.dismiss && isIterator(props.dismiss) ? props.dismiss : [];
  const onSave = props.onSave ? props.onSave : null;
  const [data, setInnerData] = React.useState(defaultValue);
  const setData = (update) => setInnerData(objectUpdate(data, update));
  const [openChild, setOpenChild] = React.useState(false);
  const [child, setChild] = React.useState(null);
  const [childTitle, setChildTitle] = React.useState(null);
  const [timedeltaUnit, setTimedeltaUnit] = React.useState({});

  const handleSave = () => {
    onSave && onSave(data);
  }

  return <Dialog fullWidth open={open} onClose={onClose}>
    <DialogTitle>{title}</DialogTitle>
    <DialogContent>
      <List style={{ width: "100%" }}>
        {Object.keys(data).map((v, k) => {
          if (dismiss.indexOf(v) >= 0) return null;
          // console.log("store.getState().types", store.getState().types);
          // console.log("typeName", typeName, "dataType", dataType);
          const args = dataType && typeName && store.getState().types && store.getState().types[typeName] &&
          store.getState().types[typeName][dataType] && store.getState().types[typeName][dataType].args &&
          store.getState().types[typeName][dataType].args[v] ?
            store.getState().types[typeName][dataType].args[v] : null;
          // console.log('v', v, 'args', args);
          if (dataType && typeName && args && !args.editable) return null;
          const showName = keyNames ? (keyNames[v] || v) : (v);
          // if (((typeof (data[v]) !== "string")) && !data[v]) return undefined;
          let value = data[v];
          if ((!value && typeof (value) !== "number") && dataType && typeName && args) {
            value = `${args.type}|${args.value ? args.value : ''}`;
          }
          // console.log('v', v, 'args', args, 'value', value);
          if (typeof (value) === 'object') {
            return <ListItem key={v} button onClick={() => {
              setChild(value);
              setChildTitle(showName);
              setOpenChild(true);
            }}>{showName}</ListItem>
          } else {
            let actionData = null;
            if (typeof (value) === "string" && value.startsWith("timezone|")) {
              // 时区暂时不可编辑
              actionData = value.slice("timezone|".length);
            } else if (typeof (value) === "string" && value.startsWith("datetime|")) {
              // console.log('datetime:', value);
              if (value === 'datetime|') {
                actionData = <Button onClick={() => {
                  setData({ [v]: `datetime|${new Date().toISOString()}` });
                }}>点击设置</Button>;
              } else {
                actionData = <ActionData value={value} onChange={e => {
                  console.log("e", e);
                  // 这里会改变到没有时区的类型
                  console.log(`datetime|${formatDateTime(e)}`);
                  setData({ [v]: `datetime|${formatDateTime(e)}` });
                }} onDelete={() => {
                  setData({ [v]: null });
                }}></ActionData>
              }
            } else if (typeof (value) === "string" && value.startsWith("timedelta|")) {
              const val = value.slice("timedelta|".length);
              const unit = timedeltaUnit[v] ? timedeltaUnit[v] : Object.keys(timedeltaUnits)[Object.keys(timedeltaUnits).length - 1];
              const updateFixed = () => {
                // const unit2 = timedeltaUnit[v] ? timedeltaUnit[v] : Object.keys(timedeltaUnits)[Object.keys(timedeltaUnits).length - 1];
                // const newValue2 = `timedelta|${parseFloat(('' + (parseFloat(data[v].slice("timedelta|".length)) / timedeltaUnits[unit2]).toFixed(2) * timedeltaUnits[unit2]))}`
                // console.log("newValue2", newValue2);
                // setData({ [v]: newValue2 });
              };
              actionData = <Box>
                <TextField value={`${parseFloat(val) / timedeltaUnits[unit]}`} onChange={e => {
                  let val = e.target.value;
                  if (isNaN(parseFloat(val)))
                    if (val.length > 0) return;
                    else val = 0;
                  const newValue = `timedelta|${parseFloat(val) * timedeltaUnits[unit]}`;
                  setData({ [v]: newValue });
                }} onBlur={updateFixed}></TextField>
                <Select value={unit}
                  onChange={e => {
                    setTimedeltaUnit(objectUpdate(timedeltaUnit, { [v]: e.target.value }));
                  }} onBlur={updateFixed}>
                  {Object.keys(timedeltaUnits).map((key, k) => <MenuItem key={key} value={key}>
                    {key}
                  </MenuItem>)}
                </Select>
              </Box>
            } else if (args && args.type === 'select' && args.options) {
              actionData = <Box style={{ display: "flex", flexDirection: 'row', justifyItems: 'center', justifyContent: 'center', alignContent: 'center' }}>
                <Box>设定值</Box>
                <Select value={value} onChange={e => {
                  setData({ [v]: e.target.value });
                }}>
                  {Object.keys(args.options).map(key => <MenuItem key={key} value={key}>{args.options[key]}</MenuItem>)}
                </Select>
                <Box>库存量</Box>
              </Box>;
            } else {
              actionData = <TextField value={`${value}`} onChange={e => {
                const newValue = typeof (value) === "number" ? getNewNumberString(e.target.value) : `${value}`;
                if (newValue === null) return;
                setData({ [v]: newValue });
              }}></TextField>;
            }
            return <ListItem key={v}>
              <ListItemText>{showName}</ListItemText>
              <ListItemSecondaryAction>
                {actionData}
              </ListItemSecondaryAction>
            </ListItem>;
          }
        }
        )}
      </List>
      {(child && childTitle) ? <ListEdit defaultValue={child} open={openChild} onClose={() => { setOpenChild(false); }} title={childTitle}></ListEdit> : undefined}
    </DialogContent>
    {onSave ? <DialogActions>
      <Button color="primary" onClick={handleSave}>保存</Button>
      <Button onClick={onClose}>取消</Button>
    </DialogActions> : <DialogActions><Box style={{ width: "100%", height: "100%", display: "flex", justifyContent: "center" }}><Typography style={{ height: "100%" }} variant="body1" color="secondary">无法保存</Typography></Box></DialogActions>}
  </Dialog>
}