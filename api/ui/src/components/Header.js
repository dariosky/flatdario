import React, {PropTypes} from 'react'
import _ from 'lodash'


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
      this.$logo.style.setProperty("--scrollparallax", scrollPosition / 2)
    }
    this.setState({ticking: false})
  }

  componentDidMount() {
    window.addEventListener('scroll',
      _.throttle(this.onScroll, 30, {trailing: true, leading: true}),
      false
    )
  }

  render() {
    const logoStyle = {
      transform: 'translateY( calc( var(--scrollparallax) * 1px ) )',
      opacity: 'calc( (200 - var(--scrollparallax)) /200 )'
    }
    return <header>
      <img id="logo" src="dist/img/dariovarotto-white.svg"
           ref={($logo) => {
             this.$logo = $logo
           }}
           style={logoStyle}
           alt="Dario Varotto"/>
      <p className="sub">
        Dreaming Electric Sheep
      </p>
      <div className="subheader">
        List of things I liked, that hopefully
        will make similar human being happier.
      </div>
    </header>
  }
}


export default Header
