import React from 'react'
import FontAwesomeIcon from '@fortawesome/react-fontawesome'
import {
  faGetPocket,
  faTumblrSquare,
  faVimeo,
  faYoutube,
} from '@fortawesome/fontawesome-free-brands'
import { faQuestionCircle, faRssSquare } from '@fortawesome/fontawesome-free-solid'
import injectSheet from 'react-jss'

const styles = {
  type: `
    position: absolute;
    padding: 3px;
    top: -2px;
    right: -10px;
    background: rgba(255, 255, 255, 1);
    border-radius: 5px;
    text-align: center;
    margin: auto;
    box-shadow: -2px 3px 11px 3px #333;

    &.fa-get-pocket {
      color: rgb(239, 68, 88); //getpocket official
    }

    &.fa-youtube {
      color: #b31217; //youtube official red: https://www.youtube.com/yt/brand/color.html
    }
`,
}

class Badge extends React.Component {
  /* A Badge with the type of the content */
  render() {
    const { type, classes } = this.props
    let icon, color

    switch (type) {
      case 'Pocket':
        color = 'rgb(239, 68, 88)' //getpocket official
        icon = faGetPocket
        break
      case 'Youtube':
        color = '#b31217' //youtube official red: https://www.youtube.com/yt/brand/color.html
        icon = faYoutube
        break
      case 'Vimeo':
        color = '#000'
        icon = faVimeo
        break
      case 'RSS':
        color = '#fbab19'
        icon = faRssSquare
        break
      case 'Tumblr':
        color = '#01273a' // tumblr official
        icon = faTumblrSquare
        break
      default:
        console.warn('Unknown item type', type)
        icon = faQuestionCircle
    }
    return (
      <FontAwesomeIcon className={classes.type} color={color} icon={icon} size="2x" />
    )
  }
}

export default injectSheet(styles)(Badge)
