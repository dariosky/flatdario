'use strict'

import React, {PropTypes} from 'react'

const itemStyle = {
  position: 'relative',
  backgroundColor: '#999',
  border: '1px solid #666',
  margin: '10px',
}

class Item extends React.Component {
  item = () => {
    let {['extra']: extraJSON, ...res} = this.props.item
    const extraObj = JSON.parse(extraJSON)
    const result = {...res, ...extraObj}
    // console.log(result)
    return result
  }

  background = () => {
    const item = this.item(),
      {type} = item
    switch (type) {
      case 'Youtube like':
        return `url(${item.thumbnails['medium']['url']})`
      case 'Pocket':
        if (item.images) return `url(${item.images[0]})`
        break
      case 'Vimeo':
        if (item.thumbnails)
          return `url(${item.thumbnails.sizes[2].link})`
        break
    }
    return ''
  }

  render() {
    const item = this.item()
    return (
      <div className="item" style={itemStyle}>
        <i className={`type ${item.type}`}/>
        <a href="" className="item-content">
          <div className="thumb"
               style={{backgroundImage: this.background()}}
          />
          <div className=" title">
            {item.title || item.url}
          </div>
        </a>
        <div className="date">
          {item.timestamp}
        </div>
      </div>
    )
  }
}

export default Item
