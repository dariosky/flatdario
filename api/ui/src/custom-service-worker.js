importScripts('https://storage.googleapis.com/workbox-cdn/releases/3.2.0/workbox-sw.js');

workbox.clientsClaim();

self.__precacheManifest = [].concat(self.__precacheManifest || []);
workbox.precaching.suppressWarnings();
workbox.precaching.precacheAndRoute(self.__precacheManifest, {});

workbox.routing.registerNavigationRoute('/index.html', {

  blacklist: [/^\/__/, /\/[^\/]+.[^\/]+$/]
});

console.info('Hello from my custom SW')

self.addEventListener('push', function (event) {
  if (event && event.data) {
    const data = event.data.json();
    console.log('Got push data:', data)
    event.waitUntil(self.registration.showNotification(data.title, {
      body: data.body,
      icon: data.icon || null
    }))
  }
});
