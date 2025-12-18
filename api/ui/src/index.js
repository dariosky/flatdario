import React from 'react'
import ReactDOM from 'react-dom'
import registerServiceWorker from './registerServiceWorker'
import App from './components/App'
import './styles/site.css'
// -- ReactRouter ---
import { BrowserRouter as Router } from 'react-router-dom'
// --- GraphQL ---
import { ApolloProvider } from 'react-apollo'
import { ApolloClient } from 'apollo-client'
import { HttpLink } from 'apollo-link-http'
import { InMemoryCache } from 'apollo-cache-inmemory'
import config from './util/config'

const httpLink = new HttpLink({ uri: config.GRAPHQL_ENDPOINT })

const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
})

// --- Init ---

let rootEl = document.getElementById('app')
ReactDOM.render(
  <ApolloProvider client={client}>
    <Router>
      <App />
    </Router>
  </ApolloProvider>,
  rootEl
)

registerServiceWorker()
