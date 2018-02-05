import React from "react"
import {graphql} from 'react-apollo'
import gql from 'graphql-tag'
import Item from './Item'

const QUERY_ITEMS = gql`
  query allItems {
    items {
      id
      type
      title
      url
      timestamp
      extra
    }
  }
`

class ItemList extends React.Component {
  render() {
    /*items = [
    {
      id: 1,
      title: 'YT item',
      type: 'youtube',
      url: 'http://xyz.com'
    },
    {
      id: 2,
      title: 'Pocket item',
      type: 'pocket',
      url: 'http://xyz.com'
    }
  ]*/
    const {allItemsQuery} = this.props

    if (allItemsQuery && allItemsQuery.loading) {
      return <div>Loading</div>
    }
    if (allItemsQuery && allItemsQuery.error) {
      return <div>Error</div>
    }
    const items = allItemsQuery.items

    const itemsBlock = items.map(
      item => <Item key={item.id} item={item}/>
    )
    return <div>
      {itemsBlock}
    </div>
  }
}

export default graphql(QUERY_ITEMS, {name: 'allItemsQuery'})(ItemList)
