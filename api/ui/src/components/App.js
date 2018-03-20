import React from "react"
import ItemList from './ItemList'
import Header from './Header'
import {Route, Switch} from 'react-router-dom'
import Search from './Search'

class App extends React.Component {
  render() {
    return [
      <Header key="header"/>,
      <Route key="search" path={["/search/:query", "/"]}>
        <Search/>
      </Route>,
      <Switch key="routes">
        <Route path="/" exact component={ItemList}/>
        <Route path="/search/:query" exact component={ItemList}/>
      </Switch>
    ]
  }
}

export default App
