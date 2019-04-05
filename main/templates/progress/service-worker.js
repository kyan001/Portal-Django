var CACHE_NAME = 'kyan001.com-progress-cache-v1'
var urlsToCache = [
    "/static/3rd/jquery/jquery-2.1.3.min.js",
    "/static/3rd/bootstrap/js/bootstrap.min.js",
    "/static/js/KyanJsUtil.js?version=1.5.1",
    "/static/3rd/bootstrap/css/bootstrap.min.css",
    "/static/css/KyanCssUtil.css?version=1.5.1",
    "/static/css/progress/list/common.css?version=2.1.1",
    "/static/css/progress/progresscard.css?version=2.3.1",
    "/static/js/progress/list/common.js?version=2.1.1",
]

self.addEventListener('install', function (event) {  // Perform install steps
    event.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            console.debug('[Service Worker] Cache Opened')
            return cache.addAll(urlsToCache)
        })
    )
})

self.addEventListener('fetch', function (event) {  // when fetch a request
    event.respondWith(caches.match(event.request).then(function (response) {
        console.debug('[Service Worker] Request Fetched: ', event.request.url)
        if (response) {  // cache hit -return response
            console.debug('[Service Worker] Request Hit: ', event.request.url)
            return response
        }
        return fetch(event.request)
    }))
})
