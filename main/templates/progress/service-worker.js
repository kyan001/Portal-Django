var CACHE_NAME = 'progress-cache-v1.1.7'
var urlsCacheFirst = [
    "/static/3rd/jquery/jquery-3.3.1.min.js",
    "/static/3rd/bootstrap-3.4.1/js/bootstrap.min.js",
    "/static/js/KyanJsUtil.js?version=1.5.1",
    "/static/3rd/bootstrap-3.4.1/css/bootstrap.min.css",
    "/static/css/KyanCssUtil.css?version=1.5.1",
    "/static/css/progress/progresslist.css?version=2.2.2",
    "/static/css/progress/progresscard.css?version=2.3.1",
    "/static/js/progress/progresslist.js?version=2.2.2",
    "/static/3rd/instant.page/instantpage-1.2.2.js",
    "/static/3rd/bootstrap-3.4.1/fonts/glyphicons-halflings-regular.woff2",
    "/static/img/Logo_List.png",
    "/progress/manifest.json",
]
var urlsOnlineFirst = [
    "/progress/list",
    "/progress/list/",
    "/progress/archive",
    "/progress/archive/",
    "/progress/search",
]

self.addEventListener('install', function (event) {  // Perform install steps
    event.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            console.debug('[Service Worker] Cache Opened:', CACHE_NAME)
            cache.addAll(pageUrls)  // non-block non-raise loading
            return cache.addAll(staticFileUrls)  // return Promise
        })
    )
})

self.addEventListener('fetch', function (event) {  // when fetch a request
    event.respondWith(caches.match(event.request).then(function (cachedResponse) {
        if (cachedResponse) {  // cache hit, return response
            cachedResponse = cleanResponseRedirect(cachedResponse)
            console.debug('[Service Worker] Response Cached:', cachedResponse.url)
            if (urlsCacheFirst.includes(removeDomainName(cachedResponse.url))) {
                console.debug("  Strategy: Cache First")
                return cachedResponse
            }
            if (urlsOnlineFirst.includes(removeDomainName(cachedResponse.url))) {
                console.debug("  Strategy: Online First")
                clonedRequest = event.request.clone()
                return fetch(clonedRequest).then(function (response) {
                    if (!response || response.status !== 200 || response.type !=='basic') {
                        console.debug("  Cached Response Returned", response)
                        postMessageToClient('oncache')
                        return cachedResponse
                    }
                    console.debug("  Online Response Returned")
                    responseToCache(event.request, response)
                    return response
                }).catch(function (err) {
                    console.debug("  Cached Response Returned", "(" + err + ")")
                    postMessageToClient('offline')
                    return cachedResponse
                })
            }
        }
        console.debug('[Service Worker] Response Uncached:', event.request.url)
        return fetch(event.request)
    }))
})

self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys().then(function (cacheNames) {
            return Promise.all(cacheNames.filter(function (cacheName) {
                if (cacheName !== CACHE_NAME) {  // delete other versions of caches
                    console.info('[Service Worker] Old Cache Deleted:', cacheName)
                    return true
                }
            }).map(function (cacheName) {
                return caches.delete(cacheName)
            }))
        })
    )
})

function cleanResponseRedirect (response) {
    if (!response.redirected) {
        return response
    }
    console.debug("[Service Worker] Response Redirected:", response.url)
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

function responseToCache (request, response) {
    var clonedResponse = response.clone()
    caches.open(CACHE_NAME).then(function (cache) {
        cache.put(request, clonedResponse)
    })
}

function removeDomainName (url) {
    return url.replace(/^.*\/\/[^\/]+/, '')
}

function postMessageToClient (messageText) {
    self.clients.matchAll().then(function (clients) {
        if (clients && clients.length) {
            clients.forEach(function (client) {
                client.postMessage(messageText)
            })
        }
    })
}
