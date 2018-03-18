import React from "react"
import {graphql} from 'react-apollo'
import gql from 'graphql-tag'
import Item from './Item'
import InfiniteScroll from 'react-infinite-scroller'
import Search from './Search'
import Loader from './utils/Loader'
import Message from './utils/Message'
import injectSheet from 'react-jss'

const QueryItems = gql`
query getItems($first:Int = 3, $cursor: String, $query:String) {
  items(first: $first, sort: TIMESTAMP_DESC, after: $cursor
        q:$query
  ) {
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

const styles = {
  aggregation: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, 320px)",
    gridGap: "2rem",
    justifyContent: "center",
    maxWidth: "1024px",
    margin: "auto",

    "&:after": {
      content: "",
      flex: "auto",
    }
  }
}

class ItemList extends React.Component {
  render() {
    const {data, loadMore, classes} = this.props

    if (data.loading) {
      return <Loader/>
    }
    if (!data) {
      return <Message color="tomato" text="No data"/>
    }
    if (data && data.error) {
      return <Message>Error</Message>
    }
    const items = data.items.edges
    const itemsBlock = items.map(
      item => <Item key={item.node.id} item={item.node}/>
    )
    const hasMore = data.items.pageInfo.hasNextPage
    return [
      <Search key="search"/>,
      <InfiniteScroll
        loadMore={loadMore}
        hasMore={hasMore}
        loader={<Loader key={0}/>}
        useCapture={{passive: true}}
        className={classes.aggregation}>
        {itemsBlock}
      </InfiniteScroll>
    ]
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

const ItemData = graphql(QueryItems, queryOptions)(
  injectSheet(styles)(ItemList)
)

export default ItemData
