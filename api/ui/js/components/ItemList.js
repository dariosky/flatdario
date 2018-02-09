import React from "react"
import {graphql} from 'react-apollo'
import gql from 'graphql-tag'
import Item from './Item'
import styles from '../../styles/social.scss'

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

class ItemList extends React.Component {
  render() {
    const {allItemsQuery} = this.props

    if (allItemsQuery && allItemsQuery.loading) {
      return <div>Loading</div>
    }
    if (allItemsQuery && allItemsQuery.error) {
      return <div>Error</div>
    }
    const items = allItemsQuery.items.edges

    const itemsBlock = items.map(
      item => <Item key={item.node.id} item={item.node}/>
    )
    return <div className={styles.aggregation}>
      {itemsBlock}
    </div>
  }
}

export default graphql(QUERY_ITEMS, {name: 'allItemsQuery'})(ItemList)
