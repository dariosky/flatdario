const urlBase64ToUint8Array = (base64String) => {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export function isSubscribeAvailable() {
  if (!('serviceWorker' in navigator)) {
    // Service Worker isn't supported on this browser, disable or hide UI.
    return false;
  }

  if (!('PushManager' in window)) {
    // Push isn't supported on this browser, disable or hide UI.
    return false;
  }
  return true
}

export function isSubscribed() {
  if (!isSubscribeAvailable()) return new Promise(
    function (resolve, reject) {
      resolve(false)
    })
  return navigator.serviceWorker.ready.then(registration => {
    return registration.pushManager.getSubscription()
      .then(function (subscription) {
        return !(subscription === null);
      });
  })
}

export function subscribeUser({applicationServerKey}) {
  return navigator.serviceWorker.ready.then(registration => {
    const subscribeOptions = {
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(
        applicationServerKey
      )
    };
    console.log('Subscribe with options', subscribeOptions)
    return registration.pushManager.subscribe(subscribeOptions)
  })
    .then(function (pushSubscription) {
      return pushSubscription;
    });
}

export function unsubscribeUser() {
  return navigator.serviceWorker.ready.then(registration => {
    return registration.pushManager.getSubscription()
      .then(function (subscription) {
        if (subscription) {
          subscription.unsubscribe();
          return subscription
        }
      })
      .then(function (subscription) {
        console.log('User is unsubscribed.', subscription);
        return subscription
      })
      .catch(function (error) {
        console.error('Error unsubscribing', error);
      });
  })
}

export function askPermission() {
  return new Promise(function (resolve, reject) {
    const permissionResult = Notification.requestPermission(function (result) {
      resolve(result);
    });

    if (permissionResult) {
      permissionResult.then(resolve, reject);
    }
  })
    .then(function (permissionResult) {
      if (permissionResult !== 'granted') {
        throw new Error('We weren\'t granted permission.');
      }
    });
}
