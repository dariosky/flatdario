import React from 'react'
import {faSearch} from '@fortawesome/fontawesome-free-solid'
import FontAwesomeIcon from '@fortawesome/react-fontawesome'
// import {StickyContainer, Sticky} from 'react-sticky'
import styles from '../../styles/social.scss'

// Sticky thanks to: https://themeteorchef.com/tutorials/react-sticky-scroll
class Sticky extends React.Component {
  render() {
    const {className, enter, exit, children} = this.props
    return (<div
      className={`Sticky ${className}`}
      data-sticky
      data-sticky-enter={enter}
      data-sticky-exit={exit}
    >
      {children}
    </div>)
  }
}


class Search extends React.Component {
  state = {query: ""}
  handleChange = (e) => {
    this.setState({query: event.target.value})
  }

  render() {
    return (
      <Sticky>
        <div className={styles.searchbar}>
          <input placeholder="Search ..."
                 value={this.state.query}
                 onChange={this.handleChange}
          />
          <FontAwesomeIcon
            color='#fff'
            icon={faSearch}
            size="2x"
          />
        </div>
      </Sticky>
    )
  }
}

export default Search
