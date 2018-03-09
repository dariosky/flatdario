import React from "react"
import {graphql} from 'react-apollo'
import gql from 'graphql-tag'
import Item from './Item'
import styles from '../../styles/social.scss'
import {Footer, Loader, Message} from './util'
import InfiniteScroll from 'react-infinite-scroller'

const QueryItems = gql`
query getItems($first:Int = 30, $cursor: String) {
  items(first: $first, sort: TIMESTAMP_DESC, after: $cursor) {
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
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
`

class ItemList extends React.Component {
  render() {
    const {data, loadMore} = this.props

    if (data.loading) {
      return <Loader/>
    }
    if (!data) {
      return <Message text="No data"/>
    }
    if (data && data.error) {
      return <div>Error</div>
    }
    const items = data.items.edges
    const itemsBlock = items.map(
      item => <Item key={item.node.id} item={item.node}/>
    )
    const hasMore = data.items.pageInfo.hasNextPage
    return <div>
      <InfiniteScroll
        loadMore={loadMore}
        hasMore={hasMore}
        loader={<Loader key={0}/>}
        useCapture={{passive: true}}
        className={styles.aggregation}>
        {itemsBlock}
      </InfiniteScroll>

      <Footer/>
    </div>
  }
}

const queryOptions = {
  options: (props) => {
    return {
      variables: {first: 9}
    }
  },
  props: ({data}) => {
    // get data from props, and return the new one
    return {
      data,
      loadMore: () => {
        return data.fetchMore({
          variables: {
            cursor: data.items.pageInfo.endCursor
          },
          updateQuery(previousResult, {fetchMoreResult}) {
            if (!fetchMoreResult.items) {
              return previousResult
            }
            const previousItems = previousResult.items.edges
            const newItems = fetchMoreResult.items.edges
            return {
              ...fetchMoreResult,
              items: {
                ...fetchMoreResult.items,
                edges: [...previousItems, ...newItems]
              }
            }
          }
        })
      }
    }
  }
}

const ItemData = graphql(QueryItems, queryOptions)(ItemList)

export default ItemData
