export function checkoutUrl(publication) {
  const c = publication.checkout;
  if (c.hosted_url) {
    const target = new URL(c.hosted_url);
    const keys = [...target.searchParams.keys()];
    const button = target.pathname === '/cgi-bin/webscr' && keys.length === 2 &&
      keys.includes('cmd') && keys.includes('hosted_button_id') &&
      target.searchParams.get('cmd') === '_s-xclick' &&
      /^[A-Z0-9]{8,32}$/.test(target.searchParams.get('hosted_button_id') || '');
    const payment = /^\/ncp\/payment\/[A-Z0-9]{8,32}$/.test(target.pathname) && !target.search;
    if (target.origin !== 'https://www.paypal.com' || target.username || target.password || target.hash || !(button || payment)) {
      throw new Error('Invalid publication PayPal link');
    }
    return c.hosted_url;
  }
  const origin = new URL(publication.canonical_url).origin;
  const target = new URL('https://www.paypal.com/cgi-bin/webscr');
  target.search = new URLSearchParams({cmd: '_xclick', business: c.merchant,
    item_name: c.item_name, item_number: c.product_id, amount: c.amount,
    currency_code: c.currency, no_shipping: '1', return: origin + c.return_path,
    cancel_return: origin + c.cancel_path}).toString();
  return target.toString();
}
