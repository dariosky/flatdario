import React from 'react'
import ReactDOM from 'react-dom'
import registerServiceWorker from './registerServiceWorker'
import App from './components/App'
import './styles/site.css'
// -- ReactRouter ---
import {BrowserRouter as Router} from 'react-router-dom'
// --- GraphQL ---
import {ApolloProvider} from 'react-apollo'
import {ApolloClient} from 'apollo-client'
import {HttpLink} from 'apollo-link-http'
import {InMemoryCache} from 'apollo-cache-inmemory'

console.info()
const env_urls = {
    // in development use the python API in another port
    development: 'http://localhost:3001/graphql'
  },
  api_url = env_urls[process.env.NODE_ENV] || '/graphql'
const httpLink = new HttpLink({uri: api_url})

const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache()
})

// --- Init ---

let rootEl = document.getElementById('app')
ReactDOM.render(
  <ApolloProvider client={client}>
    <Router>
      <App/>
    </Router>
  </ApolloProvider>,
  rootEl)
registerServiceWorker()

if (module.hot) {
  // https://medium.com/superhighfives/hot-reloading-create-react-app-73297a00dcad
  module.hot.accept('./components/App', () => {
    const NextApp = require('./components/App').default
    ReactDOM.render(
      <NextApp/>,
      rootEl
    )
  })
}
