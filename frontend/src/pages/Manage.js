import React from "react"
import Container from '@material-ui/core/Container';
import store from "../data/store";
import { setConfig, setErrorInfo, setMessage } from "../data/action";
import { api } from "../api/api";
import { Typography } from "@material-ui/core";

function Predicts(props) {
  return (<Container maxWidth="lg">
    <Typography variant="h4">管理已添加账号</Typography>
    
  </Container>)
}

export default Predicts;