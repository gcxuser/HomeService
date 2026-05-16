const apiBase = '/api';

async function request(url, method = 'GET', body = null) {
  const options = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) options.body = JSON.stringify(body);
  const resp = await fetch(url, options);
  const data = await resp.json();
  return resp.ok ? data : { error: data.detail || JSON.stringify(data) };
}

async function createUser() {
  const name = document.getElementById('userName').value;
  const phone = document.getElementById('userPhone').value;
  const result = await request(`${apiBase}/users`, 'POST', { name, phone });
  document.getElementById('userResult').textContent = JSON.stringify(result, null, 2);
}

async function addAddress() {
  const user_id = Number(document.getElementById('addressUserId').value);
  const city = document.getElementById('city').value;
  const district = document.getElementById('district').value;
  const community = document.getElementById('community').value;
  const detail_address = document.getElementById('detailAddress').value;
  const result = await request(`${apiBase}/users/${user_id}/addresses`, 'POST', {
    city,
    district,
    community,
    detail_address,
  });
  document.getElementById('addressResult').textContent = JSON.stringify(result, null, 2);
}

async function getQuote() {
  const service_type = document.getElementById('quoteServiceType').value;
  const area = Number(document.getElementById('quoteArea').value);
  const result = await request(`${apiBase}/appointments/quote`, 'POST', {
    service_type,
    area,
    extras: {},
  });
  document.getElementById('quoteResult').textContent = JSON.stringify(result, null, 2);
}

async function createOrder() {
  const user_id = Number(document.getElementById('orderUserId').value);
  const address_id = Number(document.getElementById('orderAddressId').value);
  const service_item_id = Number(document.getElementById('orderServiceItemId').value);
  const scheduled_start = document.getElementById('orderStart').value;
  const scheduled_end = document.getElementById('orderEnd').value;
  const estimated_price = Number(document.getElementById('orderEstimatedPrice').value);
  const final_price = Number(document.getElementById('orderFinalPrice').value);
  const result = await request(`${apiBase}/orders`, 'POST', {
    user_id,
    address_id,
    service_item_id,
    scheduled_start,
    scheduled_end,
    estimated_price,
    final_price,
    remark: '',
  });
  document.getElementById('orderResult').textContent = JSON.stringify(result, null, 2);
}

async function sendChat() {
  const message = document.getElementById('chatMessage').value;
  const result = await request(`${apiBase}/chat/message`, 'POST', {
    user_id: 1,
    message,
  });
  document.getElementById('chatResult').textContent = JSON.stringify(result, null, 2);
}

async function locateAddress() {
  const city = document.getElementById('mcpCity').value;
  const district = document.getElementById('mcpDistrict').value;
  const community = document.getElementById('mcpCommunity').value;
  const detail_address = document.getElementById('mcpDetail').value;
  const result = await request(`${apiBase}/mcp/locate`, 'POST', {
    city,
    district,
    community,
    detail_address,
  });
  document.getElementById('mcpResult').textContent = JSON.stringify(result, null, 2);
}
