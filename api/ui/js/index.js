import React from "react"
import ReactDOM from "react-dom"
import App from "./components/App"

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

ReactDOM.render(
  <ApolloProvider client={client}>
    <App/>
  </ApolloProvider>,
  document.getElementById("app")
)
