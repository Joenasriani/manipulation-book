const assets = {cover:'/assets/cover.jpg',scene:'/assets/collection-scene.webp',font:'/assets/fonts/manrope.ttf'};
export default function handler(req,res) {
 if (!['GET','HEAD'].includes(req.method || 'GET')) {res.setHeader('Allow','GET, HEAD');return res.status(405).end();}
 const path = assets[Array.isArray(req.query.asset) ? req.query.asset[0] : req.query.asset];
 if (!path) return res.status(404).end();
 return res.redirect(307,path);
}
