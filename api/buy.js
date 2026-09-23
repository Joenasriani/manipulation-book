import { readFileSync } from 'node:fs';
const publication = JSON.parse(readFileSync(new URL('../publication.json', import.meta.url), 'utf8'));
const c = publication.checkout;
const origin = new URL(publication.canonical_url).origin;
const checkout = new URL('https://www.paypal.com/cgi-bin/webscr');
checkout.search = new URLSearchParams({cmd:'_xclick', business:c.merchant,
 item_name:c.item_name, item_number:c.product_id, amount:c.amount,
 currency_code:c.currency, no_shipping:'1', return:origin+c.return_path,
 cancel_return:origin+c.cancel_path}).toString();
export default function handler(req, res) {
 if (!['GET','HEAD'].includes(req.method || 'GET')) {
  res.setHeader('Allow','GET, HEAD'); return res.status(405).end();
 }
 res.setHeader('Cache-Control','no-store, max-age=0');
 res.setHeader('Referrer-Policy','no-referrer');
 res.setHeader('X-Robots-Tag','noindex, nofollow');
 return res.redirect(302,checkout.toString());
}
