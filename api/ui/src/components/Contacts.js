import React from 'react'
import injectSheet from 'react-jss'
import {LinkBtn} from './NavBar'
import {faGithub, faInstagram, faLinkedin, faTwitter} from '@fortawesome/fontawesome-free-brands'

const styles = {
  block: {
    maxWidth: '1024px',
    margin: '30px auto'
  }

}

class Contacts extends React.Component {

  render() {
    const {classes} = this.props
    return (
      <div className={classes.block}>
        <h1>Here's where you can reach me...</h1>
        <div>
          Dario Varotto @ somewhere in Marbella, Spain
        </div>
        <div>
          <h2>Social profiles:</h2>
          <LinkBtn icon={faGithub}
                   style={{color: 'black'}}
                   external="https://github.com/dariosky">Github</LinkBtn>
          <LinkBtn icon={faLinkedin}
                   style={{color: 'black'}}
                   external="https://www.linkedin.com/in/dariovarotto/">Linked In</LinkBtn>
          <LinkBtn icon={faInstagram}
                   style={{color: 'black'}}
                   external="https://www.instagram.com/dariosky/">Instagram</LinkBtn>
          <LinkBtn icon={faTwitter}
                   style={{color: 'black'}}
                   external="https://twitter.com/dariosky">Twitter</LinkBtn>
        </div>

      </div>
    )
  }

}

export default injectSheet(styles)(Contacts)
