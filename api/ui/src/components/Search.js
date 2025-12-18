import React from 'react'
import { faSearch } from '@fortawesome/fontawesome-free-solid'
import FontAwesomeIcon from '@fortawesome/react-fontawesome'
import injectSheet from 'react-jss'
import withRouter from 'react-router-dom/es/withRouter'

const styles = {
  searchContainer: {
    width: '100%',
    maxWidth: '1024px',
    display: 'flex',
    margin: '0 auto',
    boxSizing: 'border-box',
    padding: '0 30px',
    justifyContent: 'flex-end',
    alignItems: 'center',
  },

  searchInput: {
    flexGrow: 1,
    width: '100%',
    margin: '10px auto',
    height: '1.2em',
    padding: '5px',
    background: '#FFF',
    color: 'black',
    fontSize: '1.2rem',
    transition: 'all 1s',
    border: '1px silver',

    '&:focus': {
      background: 'white',
    },
  },

  searchIcon: {
    verticalAlign: 'middle',
    marginLeft: '20px',
  },
}

class Search extends React.Component {
  constructor(props) {
    super(props)
    this.state = { query: '' }
  }

  componentDidMount() {
    this.componentWillReceiveProps(this.props)
  }

  componentWillReceiveProps(newProps) {
    const query = newProps.match.params.query || ''
    this.setState({ query })
  }

  handleChange = (e) => {
    const q = e.target.value,
      { history } = this.props

    this.setState({ query: q })
    if (q) history.push('/search/' + q)
    else history.push('/')
  }

  render() {
    const { classes } = this.props
    const { query } = this.state
    return (
      <div className={classes.searchBar}>
        <div className={classes.searchContainer}>
          <input
            className={classes.searchInput}
            placeholder="Search ..."
            value={query}
            onChange={this.handleChange}
          />
          <FontAwesomeIcon
            color="#fff"
            icon={faSearch}
            size="2x"
            className={classes.searchIcon}
          />
        </div>
      </div>
    )
  }
}

export default withRouter(injectSheet(styles)(Search))
