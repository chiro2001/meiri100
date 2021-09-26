import { Container, Dialog, DialogContent, DialogTitle, List, ListItem, ListItemSecondaryAction, ListItemText, Typography } from "@material-ui/core";
import React from "react";

export default function ListInfo(props) {
  const { data, open, onClose, title, keyNames } = props;
  const [openChild, setOpenChild] = React.useState(false);
  const [child, setChild] = React.useState(null);
  const [childTitle, setChildTitle] = React.useState(null);
  // console.log(data);
  // Object.keys(data).map((v, k) => { console.log(`v: ${v}, k: ${k}`) })

  return <Dialog fullWidth open={open} onClose={onClose}>
    <DialogTitle>{title}</DialogTitle>
    <DialogContent>
      <List style={{ width: "100%" }}>
        {Object.keys(data).map((v, k) => {
          const showName = keyNames ? (keyNames[v] || v) : (v);
          if (!data[v]) return undefined;
          if (typeof (data[v]) === 'object') {
            return <ListItem key={v} button onClick={() => {
              setChild(data[v]);
              setChildTitle(showName);
              setOpenChild(true);
            }}>{showName}</ListItem>
          } else {
            const s = `${data[v]}`;
            return <ListItem key={v}>
              <ListItemText>{showName}</ListItemText>
              <ListItemSecondaryAction>
                <Typography variant="body1">{s.slice(0, 20) + (s.length > 20 ? "..." : "")}</Typography>
              </ListItemSecondaryAction>
            </ListItem>
          }
        }
        )}
      </List>
      {(child && childTitle) ? <ListInfo data={child} open={openChild} onClose={() => { setOpenChild(false); }} title={childTitle}></ListInfo> : undefined}
    </DialogContent>
  </Dialog>
}