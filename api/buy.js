import { checkoutUrl } from '../lib/paypal.js';
import { readFileSync } from 'node:fs';
const publication = JSON.parse(readFileSync(new URL('../publication.json', import.meta.url), 'utf8'));
const checkout = checkoutUrl(publication);
export default function handler(req, res) {
 if (!['GET','HEAD'].includes(req.method || 'GET')) {
  res.setHeader('Allow','GET, HEAD'); return res.status(405).end();
 }
 res.setHeader('Cache-Control','no-store, max-age=0');
 res.setHeader('Referrer-Policy','no-referrer');
 res.setHeader('X-Robots-Tag','noindex, nofollow');
 return res.redirect(302,checkout);
}
