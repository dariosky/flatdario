import React from "react"
import ItemList from './ItemList'


const appStyle = {
  display: 'flex',
  flexDirection: 'row',
  flexWrap: 'wrap',
  justifyContent: 'space-between',
  alignContent: 'flex-end',
  alignItems: 'flex-end',
  backgroundColor: 'white',
  fontFamily: 'sans-serif',
  margin: '1em 3em'
}

class App extends React.Component {
  render() {
    return <ItemList style={appStyle}/>
  }
}

export default App
