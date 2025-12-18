import React from 'react'
import injectSheet from 'react-jss'
import FontAwesomeIcon from '@fortawesome/react-fontawesome'
import { faExternalLinkAlt, faPencilAlt } from '@fortawesome/fontawesome-free-solid'
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
  navRight: {
    marginLeft: 'auto',
    position: 'relative',
  },
  avatarBtn: {
    width: '38px',
    height: '38px',
    borderRadius: '50%',
    border: '1px solid rgba(255,255,255,0.3)',
    background: 'rgba(255,255,255,0.06)',
    color: 'white',
    fontWeight: 700,
    fontSize: '13px',
    cursor: 'pointer',
    textTransform: 'uppercase',
  },
  dropdown: {
    position: 'absolute',
    right: 0,
    marginTop: '10px',
    background: 'rgba(10, 12, 20, 0.95)',
    border: '1px solid rgba(255,255,255,0.15)',
    borderRadius: '12px',
    minWidth: '160px',
    boxShadow: '0 18px 40px rgba(0,0,0,0.4)',
    overflow: 'hidden',
  },
  dropdownItem: {
    display: 'block',
    width: '100%',
    padding: '10px 14px',
    background: 'transparent',
    color: '#e5e7eb',
    textAlign: 'left',
    fontSize: '14px',
    fontFamily: 'inherit',
    letterSpacing: '0.01em',
    border: 'none',
    cursor: 'pointer',
    textDecoration: 'none',
    '&:hover': {
      background: 'rgba(255,255,255,0.06)',
    },
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
  state = { isAdmin: false, initials: '', menuOpen: false }

  componentDidMount() {
    this.fetchAuth()
  }

  async fetchAuth() {
    try {
      const res = await fetch(`${config.API_BASE}auth/me`, { credentials: 'include' })
      const data = await res.json()
      if (data.authenticated && data.user) {
        const initials = data.user
          .split(/[.\s_-]+/)
          .map((p) => p[0])
          .join('')
          .slice(0, 2)
        this.setState({ isAdmin: true, initials })
      }
    } catch (e) {
      this.setState({ isAdmin: false })
    }
  }

  toggleMenu = () => {
    this.setState({ menuOpen: !this.state.menuOpen })
  }

  logout = async () => {
    await fetch(`${config.API_BASE}auth/logout`, {
      method: 'POST',
      credentials: 'include',
    })
    this.setState({ isAdmin: false, initials: '', menuOpen: false })
  }

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
        {this.state.isAdmin ? (
          <li className={classes.navRight}>
            <button className={classes.avatarBtn} onClick={this.toggleMenu}>
              {this.state.initials || 'DV'}
            </button>
            {this.state.menuOpen ? (
              <div className={classes.dropdown}>
                <a className={classes.dropdownItem} href="/new">
                  New post
                </a>
                <button className={classes.dropdownItem} onClick={this.logout}>
                  Logout
                </button>
              </div>
            ) : null}
          </li>
        ) : null}
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
