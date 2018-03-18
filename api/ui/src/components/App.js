import React from "react"
import ItemList from './ItemList'
import Header from './Header'

class App extends React.Component {
  render() {
    return [
      <Header key="header"/>,
      <ItemList key="list"/>
    ]
  }
}

export default App
