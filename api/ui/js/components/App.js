import React from "react"
import Item from './Item'


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
  constructor(props) {
    super()
  }

  render() {
    const items = [
      {
        id: 1,
        title: 'YT item',
        type: 'youtube',
        url: 'http://xyz.com'
      },
      {
        id: 2,
        title: 'Pocket item',
        type: 'pocket',
        url: 'http://xyz.com'
      }
    ]

    const itemsBlock = items.map(
      item => <Item key={item.id} item={item}/>
    )
    return <div style={appStyle}>
      {itemsBlock}
    </div>
  }
}

export default App
