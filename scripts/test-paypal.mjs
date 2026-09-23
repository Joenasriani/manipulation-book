import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { checkoutUrl } from '../lib/paypal.js';
const m = JSON.parse(readFileSync(new URL('../publication.json', import.meta.url)));
for (const link of ['https://www.paypal.com/ncp/payment/TESTBUTTON123', 'https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=TESTBUTTON123']) {
  const candidate = structuredClone(m); candidate.checkout.hosted_url = link;
  assert.equal(checkoutUrl(candidate), link);
}
for (const link of ['https://paypal.com.example.com/ncp/payment/TESTBUTTON123', 'http://www.paypal.com/ncp/payment/TESTBUTTON123', 'https://www.paypal.com/ncp/payment/TESTBUTTON123#fragment', 'https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=TESTBUTTON123&amount=0.01', 'https://www.paypal.com/ncp/payment/TESTBUTTON123?amount=0.01']) {
  const candidate = structuredClone(m); candidate.checkout.hosted_url = link;
  assert.throws(() => checkoutUrl(candidate));
}
console.log('PASS: accepted official product links and rejected substituted origins or parameters');
