import store from "../data/store";


class WebSocketAPI {
  constructor(url) {
    this.connect = this.connect.bind(this);
    this.url = url || store.getState().config.data.remote_login.server || "ws://127.0.0.1:8081";
    this.ws = null;
    this.onopen = () => {
      console.log('Connection started');
    };
    this.ondata = e => {
      if (e.cmd === 'code') {
        this.oncode(e.data);
      } else if (e.cmd === 'cookies') {
        this.oncookies(e.data);
      }
    };
    this.onmessage = e => {
      // console.log('onmessage', e);
      this.ondata(JSON.parse(e.data));
    };
    this.onerror = e => {
      console.error(e);
    };
    this.onclose = () => {
      console.log('Connection closed');
    };
    this.oncode = code => { console.log('code', code); }
    this.oncookies = cookies => { console.log('cookies', cookies); }
  }
  connect() {
    this.ws = this.ws || new WebSocket(this.url);
    this.ws.onopen = this.onopen;
    this.ws.onclose = this.onclose;
    this.ws.onerror = this.onerror;
    this.ws.onmessage = this.onmessage;
  }
  close() {
    if (this.ws) this.ws.close();
  }
}

export { WebSocketAPI };