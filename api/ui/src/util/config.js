// the public server key for push notifications

const DEV_BASE =
  typeof window !== 'undefined'
    ? `${window.location.protocol}//${window.location.hostname}:3001/`
    : 'http://127.0.0.1:3001/'
const ENV_URLS = {
  // in development use the python API in another port
  development: DEV_BASE,
}
const API_BASE = ENV_URLS[process.env.NODE_ENV] || '/'

const config = {
  GRAPHQL_ENDPOINT: API_BASE + 'graphql',
  APPLICATION_SERVER_KEY:
    'BAtYqi2RowWBPHZfUUs0ypHfJ6lCpeiMCWVxUxd' +
    'Zuhap5rBj6m7ngRE7o2ADn_bqkCCF5WKJuvrTRqMCRDDffak',
  PUSH_SUBSCRIBE_ENDPOINT: API_BASE + 'push/subscribe',
  PUSH_UNSUBSCRIBE_ENDPOINT: API_BASE + 'push/unsubscribe',
  API_BASE,
}

export default config
