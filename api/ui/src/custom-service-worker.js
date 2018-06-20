/*
workbox.clientsClaim();

self.__precacheManifest = [].concat(self.__precacheManifest || []);
workbox.precaching.suppressWarnings();
workbox.precaching.precacheAndRoute(self.__precacheManifest, {});

workbox.routing.registerNavigationRoute('/index.html', {

  blacklist: [/^\/__/, /\/[^\/]+.[^\/]+$/]
});

*/
console.info('Hello from my custom service worker')

self.addEventListener('push', function (event) {
  console.log('push-event', event)
  if (event && event.data) {
    const data = event.data.json();
    console.log('Got push data:', data)
    event.waitUntil(
      self.registration.showNotification(
        data.title, {
          body: data.body,
          image: data.image || null,
          icon: data.icon || '/favicon.ico'
        }))
  }
  else {
    console.log('Push event without data')
  }
});

