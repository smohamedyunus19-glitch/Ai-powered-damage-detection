/* FIX NEARBY — API HELPER */
const ApiService = {
  base: 'http://localhost:5000/api',
  async upload(file, deviceType) {
    const form = new FormData();
    form.append('file', file); form.append('device_type', deviceType);
    return fetch(`${this.base}/upload`, {method:'POST',body:form}).then(r=>r.json());
  },
  async predict(filename, deviceType, lat, lng) {
    return fetch(`${this.base}/predict`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({filename, device_type:deviceType, latitude:lat, longitude:lng})
    }).then(r=>r.json());
  },
  async shops(lat, lng, deviceType) {
    return fetch(`${this.base}/shops?lat=${lat}&lng=${lng}&device_type=${deviceType}`).then(r=>r.json());
  }
};
