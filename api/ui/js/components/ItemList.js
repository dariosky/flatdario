import React from "react"
import {graphql} from 'react-apollo'
import gql from 'graphql-tag'
import Item from './Item'
import styles from '../../styles/social.scss'
import {SyncLoader} from 'react-spinners'

const QUERY_ITEMS = gql`
 query allItems {
  items(first:30, sort:TIMESTAMP_DESC) {
    edges {
      node {
        id
        type
        title
        url
        timestamp
        extra
      }
    }
  }
}
`

class LoadMoreBtn extends React.Component {
  render() {
    return <div className={styles.btn} onClick={this.props.onClick}>
      Load More
    </div>
  }
}


const Footer = () => {
  const year = (new Date()).getFullYear()
  return <div className={styles.footer}>
    <a href="https://creativecommons.org/licenses/by/4.0/">CC-BY</a>
    Dario Varotto {year}
  </div>
}

class ItemList extends React.Component {
  loadMore = () => {
    console.log("Loading more")
  }

  render() {
    const {allItemsQuery} = this.props

    if (allItemsQuery && allItemsQuery.loading) {
      return <div className={styles.loader}>
        <SyncLoader
          color={'#777'}
        />
      </div>
    }
    if (allItemsQuery && allItemsQuery.error) {
      return <div>Error</div>
    }
    const items = allItemsQuery.items.edges

    const itemsBlock = items.map(
      item => <Item key={item.node.id} item={item.node}/>
    )
    return [
      <div className={styles.aggregation}>
        {itemsBlock}
      </div>,
      <LoadMoreBtn onClick={this.loadMore}/>,

      <Footer/>
    ]
  }
}

export default graphql(QUERY_ITEMS, {name: 'allItemsQuery'})(ItemList)
