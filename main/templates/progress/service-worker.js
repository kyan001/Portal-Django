var CACHE_NAME = 'kyan001.com-progress-cache-v1.0.0'
var urlsToCache = [
    "/progress/list",
    "/static/3rd/jquery/jquery-3.3.1.min.js",
    "/static/3rd/bootstrap-3.4.1/js/bootstrap.min.js",
    "/static/js/KyanJsUtil.js?version=1.5.1",
    "/static/3rd/bootstrap-3.4.1/css/bootstrap.min.css",
    "/static/css/KyanCssUtil.css?version=1.5.1",
    "/static/css/progress/list/common.css?version=2.1.1",
    "/static/css/progress/progresscard.css?version=2.3.1",
    "/static/js/progress/list/common.js?version=2.1.1",
    "/static/3rd/instant.page/instantpage-1.2.2.js",
    "http://localhost:8000/static/3rd/bootstrap-3.4.1/fonts/glyphicons-halflings-regular.woff2",
]

self.addEventListener('install', function (event) {  // Perform install steps
    event.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            console.debug('[Service Worker] Cache Opened:', CACHE_NAME)
            return cache.addAll(urlsToCache)  // return Promise
        })
    )
})

self.addEventListener('fetch', function (event) {  // when fetch a request
    event.respondWith(caches.match(event.request).then(function (response) {
        if (response) {  // cache hit, return response
            console.debug('[Service Worker] Request Hit:', response.url)
            if (response.redirected) {
                console.debug("[Service Worker] Response Redirected:", response.url)
                return cleanResponseRedirect(response)
            }
            return response
        }
        console.debug('[Service Worker] Request Miss:', event.request.url)
        return fetch(event.request)
        /* cache all uncached response
        var fetchRequest = event.request.clone()
        return fetch(fetchRequest).then(function (response) {
            if (!response || response.status !== 200 || response.type !=='basic') {
                return response
            }
            var responseToCache = response.clone()
            caches.open(CACHE_NAME).then(function (cache) {
                cache.put(event.request, responseToCache)
            })
            return response
        })
        */
    }))
})

self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys().then(function (cacheNames) {
            return Promise.all(cacheNames.map(function (cacheName) {
                if (cacheName !== CACHE_NAME) {  // delete old version Service Worker caches
                    console.debug('[Service Worker] Old Cache Deleted:', cacheName)
                    return caches.delete(cacheName);
                }
            }))
        })
    )
})

function cleanResponseRedirect (response) {
    const clonedResponse = response.clone()
    const bodyPromise = 'body' in clonedResponse
        ? Promise.resolve(clonedResponse.body)
        : clonedResponse.blob()  // browers does not support response.body
    return bodyPromise.then(function (body) {
        return new Response(body, {
            headers: clonedResponse.headers,
            status: clonedResponse.status,
            statusText: clonedResponse.statusText
        })
    })
}
