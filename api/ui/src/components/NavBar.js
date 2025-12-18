import React from 'react'
import injectSheet from 'react-jss'
import FontAwesomeIcon from '@fortawesome/react-fontawesome'
import {
  faExternalLinkAlt,
  faPencilAlt,
} from '@fortawesome/fontawesome-free-solid'
import { Link } from 'react-router-dom'
import SubscribeBtn from './SubscriptionBtn'
import config from '../util/config'

const styles = {
  navbar: {
    maxWidth: '1024px',
    margin: '0 auto',
    padding: '0 30px',
    listStyle: 'none',
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    justifyContent: 'left',
  },

  li: {
    margin: '5px',
  },

  link: {
    padding: '5px 15px',
    transition: 'all .3s ease',

    '&:hover': {
      backgroundColor: '#666',
      color: 'white',
    },
  },

  icon: {
    verticalAlign: '-2px',
    marginRight: '7px',
  },

  brand: {
    display: 'flex',
    alignItems: 'center',
    padding: '6px 12px',
    marginRight: '6px',
    borderRadius: '10px',
    background: 'rgba(255,255,255,0.06)',
    boxShadow: '0 6px 12px rgba(0,0,0,0.25)',
  },
  brandImg: {
    height: '22px',
    width: '22px',
    marginRight: '8px',
    verticalAlign: 'middle',
    transform: 'translateY(-2px)',
    filter: 'invert(1) brightness(2.5)',
  },
}

const LinkBtn = injectSheet(styles)(
  ({ title, url, external, children, icon, classes, ...rest }) => {
    return external ? (
      <li className={classes.li}>
        <a href={external} className={classes.link} {...rest} target="_blank">
          <FontAwesomeIcon icon={icon || faExternalLinkAlt} className={classes.icon} />
          {children}
        </a>
      </li>
    ) : (
      <li className={classes.li} {...rest}>
        <Link to={url} className={classes.link}>
          {children}
        </Link>
      </li>
    )
  }
)

class NavBar extends React.Component {
  render() {
    const { classes } = this.props
    return (
      <ul className={classes.navbar}>
        <LinkBtn url="/#">
          <img src="/img/dv.svg" alt="DV" className={classes.brandImg} />
          Home
        </LinkBtn>
        <LinkBtn external="https://home.dariosky.it">Starting Page</LinkBtn>
        <LinkBtn url="/contacts">
          <FontAwesomeIcon icon={faPencilAlt} className={classes.icon} />
          Contacts
        </LinkBtn>

        <SubscribeBtn applicationServerKey={config.APPLICATION_SERVER_KEY} />
      </ul>
    )
  }
}

const fixedStyles = {
  fixed: {
    position: 'sticky',
    backgroundColor: 'black',
    top: 0,
    width: '100%',
    zIndex: 3,
    padding: '10px 0',
    boxShadow:
      '0 2px 4px -1px rgba(0, 0, 0, 0.2), ' +
      '0 4px 5px 0px rgba(0, 0, 0, 0.14),' +
      ' 0 1px 10px 0px rgba(0, 0, 0, 0.12)',
  },
}
const Fixed = injectSheet(fixedStyles)(({ children, classes }) => {
  return <div className={classes.fixed}>{children}</div>
})

export { Fixed, LinkBtn }
export default injectSheet(styles)(NavBar)
