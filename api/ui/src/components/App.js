import React from "react"
import ItemList from './ItemList'
import Header from './Header'
import {Route, Switch} from 'react-router-dom'
import Search from './Search'
import NavBar, {Fixed} from './NavBar'
import Contacts from './Contacts'

class App extends React.Component {
  render() {
    return [
      <Header key="header"/>,
      <Fixed key="fixed">
        <NavBar key="nav"/>
        <Switch key="search">
          <Route path="/" exact component={Search}/>
          <Route path="/search/:query" exact component={Search}/>
        </Switch>
      </Fixed>,

      <Switch key="routes">
        <Route path="/" exact component={ItemList}/>
        <Route path="/search/:query" exact component={ItemList}/>
        <Route path="/contacts" exact component={Contacts}/>
      </Switch>,
    ]
  }
}

export default App
