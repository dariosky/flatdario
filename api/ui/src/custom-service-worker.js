workbox.clientsClaim();

self.__precacheManifest = [
  {url: '/img/dariovarotto-white.svg', revision: 'v1'},
  {url: '/img/coding-bkg.jpg', revision: 'v1'},
  {url: 'https://fonts.googleapis.com/css?family=Open+Sans', revision: 'v1'}
].concat(self.__precacheManifest);

workbox.precaching.suppressWarnings();
workbox.precaching.precacheAndRoute(self.__precacheManifest, {});

workbox.routing.registerNavigationRoute('/index.html', {

  blacklist: [/^\/__/, /\/[^\/]+.[^\/]+$/]
});

console.info('Hello from my custom service worker')

const siteUrl = new URL(self.location.origin).href;

self.addEventListener('push', function (event) {
  console.log('push-event', event)
  if (event && event.data) {
    const data = event.data.json();
    console.log('Got push data:', data)

    event.waitUntil(
      self.registration.showNotification(
        data.title, {
          body: data.body,
          image: data.image,
          icon: data.icon || '/favicon.ico',
          requireInteraction: true,
          tag: 'toMainSite'
        }))
  }
  else {
    console.log('Push event without data')
  }
});


self.addEventListener('notificationclick', function (event) {
  const clickedNotification = event.notification;
  clickedNotification.close();

  // Do something as the result of the notification click
  const promiseChain = clients.openWindow(siteUrl);
  event.waitUntil(promiseChain);
});

