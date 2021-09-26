import React from "react"
import Container from '@material-ui/core/Container';
import { Button, MenuItem, FormControl, InputLabel, List, ListItem, ListItemSecondaryAction, ListItemText, Select, ListSubheader, Switch, Dialog, DialogTitle, DialogContent, Typography, DialogActions, FormControlLabel, Checkbox, Divider, Box, Grid, TextField, IconButton } from "@material-ui/core";
import { Table, TableBody, TableCell, TableRow } from "@material-ui/core";
import HelpOutlineIcon from '@material-ui/icons/HelpOutline';
import store from "../data/store";
import { setConfig, setErrorInfo, setMessage } from "../data/action";
import { api } from "../api/api";

function Predicts(props) {
  const [useSpan, setUseSpan] = React.useState(false);
  const [openHelp, setOpenHelp] = React.useState(false);
  const labels = ['小包最低价', '小包最高价', '中包最低价', '中包最高价', '大包最低价', '大包最高价'];
  const labelShows = { '小包最低价': '小包(闲时)', '小包最高价': '小包(黄金时段)', '中包最低价': '中包(闲时)', '中包最高价': '中包(黄金时段)', '大包最低价': '大包(闲时)', '大包最高价': '大包(黄金时段)' };
  const [predictsResult, setPredictsResult] = React.useState(null);
  const defaultValues = [
    ['66', '76'], ['76', '86'], ['86', '96'], ['96', '106'], ['116', '126'], ['126', '146']
  ]
  const labelsTemp = labels.map((v, k) => {
    return { [v]: defaultValues[k] };
  });
  const labelValues = ((() => {
    let temp = {};
    for (const item of labelsTemp)
      for (const k in item)
        temp[k] = item[k];
    return temp;
  })());
  // console.log(labelValues);
  const [inputValues, setInputValues] = React.useState(labelValues);
  const getTempValues = () => {
    let tempValues = {};
    for (const k in inputValues) tempValues[k] = inputValues[k];
    return tempValues;
  }

  const items = labels.map((v, k) => {
    return useSpan ?
      <ListItem key={v}>
        <ListItemText primary={labelShows[v]}></ListItemText>
        <ListItemSecondaryAction>
          <Box>
            <TextField style={{ maxWidth: 40 }} inputProps={{ style: { textAlign: "center" } }} value={inputValues[v][0]} onChange={e => {
              let tmp = getTempValues();
              tmp[v][0] = e.target.value;
              setInputValues(tmp);
            }}></TextField>~
            <TextField style={{ maxWidth: 40 }} inputProps={{ style: { textAlign: "center" } }} value={inputValues[v][1]} onChange={e => {
              let tmp = getTempValues();
              tmp[v][1] = e.target.value;
              setInputValues(tmp);
            }}></TextField>
          </Box>
        </ListItemSecondaryAction>
      </ListItem> :
      <ListItem key={v}>
        <ListItemText primary={labelShows[v]}></ListItemText>
        <ListItemSecondaryAction>
          <TextField style={{ maxWidth: 90 }} inputProps={{ style: { textAlign: "center" } }} fullWidth value={inputValues[v][0]} onChange={e => {
            let tmp = getTempValues();
            tmp[v][0] = e.target.value;
            setInputValues(tmp);
          }}></TextField>
        </ListItemSecondaryAction>
      </ListItem >;
  });
  const content = <List>
    {items}
  </List>;
  const handlePredicts = () => {
    // 检查数据
    let tempValues = getTempValues();
    if (!useSpan)
      for (const k in tempValues)
        tempValues[k] = [tempValues[k][0],]
    for (const k in tempValues) {
      for (let i = 0; i < tempValues[k].length; i++) {
        let val = null;
        try {
          val = parseFloat(tempValues[k][i]);
        } catch (e) {
          store.dispatch(setErrorInfo(`数值错误: ${tempValues[k][i]}, ${e}`));
          return;
        }
        if (!val && val !== 0) {
          store.dispatch(setErrorInfo(`数值错误: ${tempValues[k][i]}`));
          return;
        }
        tempValues[k][i] = val;
      }
    }
    console.log(JSON.stringify(tempValues));
    // api.predicts(tempValues).then(d => {
    //   console.log(d);
    //   setPredictsResult(d.data);
    // });
    api.request("predicts", 'POST', { predict_data: tempValues }).then(d => {
      console.log(d);
      setPredictsResult(d.data);
    });
  };
  const result = !predictsResult ? null : <Table>
    <TableBody>
      {useSpan ? <TableRow>
        <TableCell align="center" colSpan={2}>预测曝光人数</TableCell>
        <TableCell align="center" colSpan={2}>预测访问人数</TableCell>
        <TableCell align="center" colSpan={2}>预测下单人数</TableCell>
      </TableRow> : <TableRow>
        <TableCell align="center">预测曝光人数</TableCell>
        <TableCell align="center">预测访问人数</TableCell>
        <TableCell align="center">预测下单人数</TableCell>
      </TableRow>}
      {useSpan ? <TableRow>
        <TableCell align="center">{parseInt(predictsResult['visible'][0])}</TableCell>
        <TableCell align="center">{parseInt(predictsResult['visible'][1])}</TableCell>
        <TableCell align="center">{parseInt(predictsResult['visit'][0])}</TableCell>
        <TableCell align="center">{parseInt(predictsResult['visit'][1])}</TableCell>
        <TableCell align="center">{parseInt(predictsResult['order'][0])}</TableCell>
        <TableCell align="center">{parseInt(predictsResult['order'][1])}</TableCell>
      </TableRow> : <TableRow>
        <TableCell align="center">{parseInt(predictsResult['visible'][0])}</TableCell>
        <TableCell align="center">{parseInt(predictsResult['visit'][0])}</TableCell>
        <TableCell align="center">{parseInt(predictsResult['order'][0])}</TableCell>
      </TableRow>}
    </TableBody>
  </Table>;
  return (<Container maxWidth="sm">
    <Typography variant="h4">根据标准数据集预测</Typography>
    <Box>
      <FormControlLabel control={<Checkbox onChange={e => {
        setUseSpan(e.target.checked);
        setPredictsResult(null);
      }} checked={useSpan} color="secondary" />} label="使用数据区间" />
      <IconButton onClick={() => setOpenHelp(true)}>
        <HelpOutlineIcon></HelpOutlineIcon>
      </IconButton>
    </Box>
    <Divider></Divider>
    {content}
    <Button fullWidth variant="contained" color="secondary" onClick={handlePredicts}>预测</Button>
    <Divider></Divider>
    {result}
    <Dialog open={openHelp} onClose={() => { setOpenHelp(false); }}>
      <DialogTitle>帮助信息</DialogTitle>
      <DialogContent>
        <Typography variant="h6">使用数据区间</Typography>
        <Typography variant="body1">使用数据区间可以输入数据上下限，并且预测出对应参数的上下限，帮助您更好地界定您的数据。</Typography>
        <Typography variant="h6">价格说明</Typography>
        <Typography variant="body1">“黄金时段”价格为节假日、夜间等适合高定价的时段，“闲时”为除此之外的时段。输入价格为不加入酒水等的基础价格。</Typography>
        <Typography variant="h6">预测结果说明</Typography>
        <Typography variant="body1">预测结果基于当前已有数据集数据，预测准确性不能百分百保证。更新数据集等功能将在后续版本上线。</Typography>
      </DialogContent>
      <DialogActions>
        <Button color="primary" onClick={() => { setOpenHelp(false); }}>了解</Button>
      </DialogActions>
    </Dialog>
  </Container>)
}

export default Predicts;