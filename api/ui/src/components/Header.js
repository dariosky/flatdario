import React from 'react'
import _ from 'lodash'
import injectSheet from 'react-jss'

const styles = {
  header: {
    color: '#eee',
    minHeight: '50vh',
    position: 'relative',
    background: 'black no-repeat 50%',
    backgroundImage: `url(/img/coding-bkg.jpg)`,
    backgroundSize: 'cover',
    padding: '15px 10px',
    display: 'flex',
    flexDirection: 'column',
    textAlign: 'center'
  },

  logo: `
    width: 90%;
    max-width: 600px;
    margin: auto;
    display: block;
    transform: translateY( calc( var(--scrollparallax) * 1px ) );
    opacity: calc( (200 - var(--scrollparallax)) /200 );
    will-change: transform, opacity;
  `,

  sub: `font-size: larger;`
}

class Header extends React.Component {
  state = {
    scrollPosition: 0,
    ticking: false,
    $logo: null
  }

  onScroll = () => {
    const newState = {scrollPosition: window.scrollY}
    this.setState(newState)
    this.requestTick()
  }

  requestTick = () => {
    const {ticking} = this.state
    if (!ticking) {
      window.requestAnimationFrame(this.update)
    }
    this.setState({ticking: true})
  }

  update = () => {
    if (this.$logo) {
      const {scrollPosition} = this.state
      this.$logo.style.setProperty('--scrollparallax', scrollPosition / 2)
    }
    this.setState({ticking: false})
  }

  componentDidMount() {
    window.addEventListener('scroll',
      _.throttle(this.onScroll, 10, {trailing: true, leading: true}),
      false
    )
  }

  render() {
    const {classes} = this.props
    return <header className={classes.header}>
      <img className={classes.logo} src="/img/dariovarotto-white.svg"
           ref={($logo) => {
             this.$logo = $logo
           }}
           alt="Dario Varotto"/>
      <p className={classes.sub}>
        Dreaming Electric Sheep
      </p>
      <div className="subheader">
        List of things I liked, that hopefully
        will make similar human being happier.
      </div>
    </header>
  }
}

export default injectSheet(styles)(Header)
