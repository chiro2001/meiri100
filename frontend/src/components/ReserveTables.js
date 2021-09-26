import React from 'react'
import { LinearProgress, Button, Container, Dialog, DialogTitle, IconButton } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import PropTypes from 'prop-types';
import AppBar from '@material-ui/core/AppBar';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import CloseIcon from '@material-ui/icons/Close';
import VisibilityIcon from '@material-ui/icons/Visibility';
import FullscreenIcon from '@material-ui/icons/Fullscreen';
import FullscreenExitIcon from '@material-ui/icons/FullscreenExit';
import ReserveTable from './ReserveTable';
import { weekDayList } from '../utils/utils';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`scrollable-auto-tabpanel-${index}`}
      aria-labelledby={`scrollable-auto-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box>
          {/* <Typography>{children}</Typography> */}
          {children}
        </Box>
      )}
    </div>
  );
}

TabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.any.isRequired,
  value: PropTypes.any.isRequired,
};

const useStyles = makeStyles((theme) => ({
  root: {
    overflowX: 'auto',
    display: 'block',
    width: '100%',
    flexGrow: 1,
    width: '100%',
    backgroundColor: theme.palette.background.paper,
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 120,
  },
  selectEmpty: {
    marginTop: theme.spacing(2),
  },
}));

function a11yProps(index) {
  return {
    id: `scrollable-auto-tab-${index}`,
    'aria-controls': `scrollable-auto-tabpanel-${index}`,
  };
}

export default function ReserveTables(props) {
  const classes = useStyles();
  const [tabValue, setTableValue] = React.useState(new Date().getDay());
  const [showTable, setShowTable] = React.useState(false);
  const [fullShow, setFullShow] = React.useState(false);
  const handleChange = (event) => {
    setTableValue(event.target.value);
  };
  const table = <div className={classes.root}>
    <Tabs
      value={tabValue}
      onChange={(e, val) => setTableValue(val)}
      indicatorColor="primary"
      textColor="primary"
      variant="scrollable"
      scrollButtons="auto"
      aria-label="scrollable auto tabs example"
    >
      {["日", '一', '二', '三', '四', '五', '六'].map((d, i) => {
        return (<Tab label={'周' + d} key={d} {...a11yProps(i)} />);
      })}
    </Tabs>
    {[0, 1, 2, 3, 4, 5, 6].map((d, i) => <TabPanel key={d} value={tabValue} index={d}>
      <ReserveTable day={tabValue}></ReserveTable>
    </TabPanel>)}
  </div>;
  return (
    // <Container className={classes.root}>
    <div>
      <FormControl className={classes.formControl}>
        <InputLabel>选择日期</InputLabel>
        <Select
          value={tabValue}
          onChange={handleChange}
        >
          {weekDayList.map((d, i) => <MenuItem key={d} value={i}>{'周' + d}</MenuItem>)}
        </Select>
      </FormControl>
      <IconButton style={{ float: 'right' }} variant="contained" onClick={() => {
        setShowTable(true);
        setFullShow(true);
      }}><FullscreenIcon /></IconButton>
      { window.innerWidth >= 600 ? table : <Button fullWidth variant="contained" onClick={() => { setShowTable(!showTable); }}>点击{showTable ? "隐藏" : "显示"}表格</Button>}
      <Dialog fullScreen={fullShow} onClose={() => { setShowTable(false); }} open={showTable}>
        <DialogTitle>
          <Box component="span">周{weekDayList[tabValue]}({new Date().setDay(tabValue).toDateString()})数据</Box>
          {fullShow ? <IconButton edge="end" style={{ float: 'right' }} onClick={() => {
            setFullShow(false);
            setShowTable(false);
          }}><FullscreenExitIcon /></IconButton> : <IconButton style={{ float: 'right' }} variant="contained" onClick={() => {
            setShowTable(true);
            setFullShow(true);
          }}><FullscreenIcon /></IconButton>}</DialogTitle>
        {table}
      </Dialog>
      {/* </Container > */}
    </div>
  );

}

