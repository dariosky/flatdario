'use strict'

import React, {PropTypes} from 'react'
import FontAwesomeIcon from '@fortawesome/react-fontawesome'
import {
  faGetPocket, faVimeo,
  faYoutube, faTumblrSquare
} from '@fortawesome/fontawesome-free-brands'
import {faQuestionCircle} from '@fortawesome/fontawesome-free-solid'
import styles from '../../styles/social.scss'
import {faRssSquare} from '@fortawesome/fontawesome-free-solid'


class Badge extends React.Component {
  /* A Badge with the type of the content */
  render() {
    const {type} = this.props
    let icon, color

    switch (type) {
      case "Pocket":
        color = "rgb(239, 68, 88)" //getpocket official
        icon = faGetPocket
        break
      case "Youtube like":
        color = "#b31217" //youtube official red: https://www.youtube.com/yt/brand/color.html
        icon = faYoutube
        break
      case "Vimeo":
        color = "#000"
        icon = faVimeo
        break
      case "RSS":
        color = '#fbab19'
        icon = faRssSquare
        break
      case "Tumblr":
        color = "#01273a" // tumblr official
        icon = faTumblrSquare
        break
      default:
        console.warn("Unknown item type", type)
        icon = faQuestionCircle
    }
    return <FontAwesomeIcon className={styles.type}
                            color={color}
                            icon={icon}
                            size="3x"
    />
  }
}

class Item extends React.Component {
  item = () => {
    let {['extra']: extraJSON, ...res} = this.props.item
    const extraObj = JSON.parse(extraJSON)
    return {...res, ...extraObj}
  }

  background = () => {
    const item = this.item(),
      {type} = item
    switch (type) {
      case 'Youtube like':
        return `url(${item.thumbnails['medium']['url']})`
      case 'Pocket':
        if (item.images) return `url(${item.images[0] || ''})`
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
    return <div className={styles.item}>
      <Badge type={item.type}/>
      <a href={item.url} target="_blank" className="item-content">
        <div className={styles.thumb}
             style={{backgroundImage: this.background()}}
        />
        <div className={styles.title}>
          {item.title || item.url}
        </div>
      </a>
      <div className={styles.date}>
        {item.timestamp}
      </div>
    </div>

  }
}

export default Item
