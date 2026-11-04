// 서비스 워커: 앱 파일을 폰에 저장해 두고 인터넷 없이도 실행되게 한다.
// 앱 내용을 고치면 VERSION 숫자를 올려야 폰에서 새 버전을 받는다.
const VERSION = 'travel-talk-v3';
const FONTS = 'travel-talk-fonts';
const FILES = ['./', 'index.html', 'manifest.json', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'];

// 설치할 때 앱 파일을 모두 캐시에 담는다
self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

// 옛 버전 캐시는 지운다 (글꼴 캐시는 그대로 둔다)
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== VERSION && k !== FONTS).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET') return;
  // 구글 글꼴: 한 번 받은 글꼴은 저장해 두고 오프라인에서도 쓴다
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(caches.open(FONTS).then(c => c.match(req).then(hit => hit || fetch(req).then(res => {
      if (res.ok || res.type === 'opaque') c.put(req, res.clone());
      return res;
    }))));
    return;
  }
  if (url.origin !== location.origin) return;
  // 화면(HTML)은 인터넷을 먼저 시도해 최신으로, 안 되면 저장본
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req)
      .then(res => { const copy = res.clone(); caches.open(VERSION).then(c => c.put('./', copy)); return res; })
      .catch(() => caches.match('./')));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
});
