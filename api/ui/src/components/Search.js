import React from 'react'
import {faSearch} from '@fortawesome/fontawesome-free-solid'
import FontAwesomeIcon from '@fortawesome/react-fontawesome'
import injectSheet from 'react-jss'


const styles = {
  searchBar: {
    position: 'sticky',
    top: 0,
    width: '100%',
    margin: 0,
    textAlign: 'right',
    background: 'black',
    zIndex: 3,
    padding: '1em 0',
    boxShadow: '0 2px 4px -1px rgba(0, 0, 0, 0.2), ' +
    '0 4px 5px 0px rgba(0, 0, 0, 0.14),' +
    ' 0 1px 10px 0px rgba(0, 0, 0, 0.12)',
  },
  searchInput: {
    width: "33%",
    height: "1.2em",
    padding: "5px",
    background: "#CCC",
    color: "black",
    fontSize: "1.2rem",
  },

  searchIcon: {
    verticalAlign: 'middle',
    margin: '0 30px',
  }
}

class Search extends React.Component {
  state = {query: ""}
  handleChange = (e) => {
    this.setState({query: e.target.value})
  }

  render() {
    const {classes} = this.props
    return (
      <div className={classes.searchBar}>
        <input className={classes.searchInput}
               placeholder="Search ..."
               value={this.state.query}
               onChange={this.handleChange}
        />
        <FontAwesomeIcon
          color='#fff'
          icon={faSearch}
          size="2x"
          className={classes.searchIcon}
        />
      </div>
    )
  }
}

export default injectSheet(styles)(Search)
