import React from 'react'
import ReactDOM from 'react-dom'
import registerServiceWorker from './registerServiceWorker'
import App from './components/App'
import './styles/site.css'
// -- ReactRouter ---
import {BrowserRouter} from 'react-router-dom'

// --- GraphQL ---
import {ApolloProvider} from 'react-apollo'
import {ApolloClient} from 'apollo-client'
import {HttpLink} from 'apollo-link-http'
import {InMemoryCache} from 'apollo-cache-inmemory'

const httpLink = new HttpLink({uri: 'http://127.0.0.1:3001/graphql'})

const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache()
})

// --- Init ---

let rootEl = document.getElementById('app')
ReactDOM.render(
  <ApolloProvider client={client}>
    <BrowserRouter>
      <App/>
    </BrowserRouter>
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
