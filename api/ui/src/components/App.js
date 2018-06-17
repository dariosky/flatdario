import React from 'react'
import ItemList from './ItemList'
import Header from './Header'
import {Route, Switch} from 'react-router-dom'
import Search from './Search'
import NavBar, {Fixed} from './NavBar'
import Contacts from './Contacts'
import withTracker from '../analytics/withTracker'
import ReactGA from 'react-ga'
// Hot-loader
import {hot} from 'react-hot-loader'

ReactGA.initialize('UA-62120-5')

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
        <Route path="/" exact component={withTracker(ItemList)}/>
        <Route path="/search/:query" exact component={withTracker(ItemList)}/>
        <Route path="/contacts" exact component={withTracker(Contacts)}/>
      </Switch>
    ]
  }
}

export default hot(module)(App)
