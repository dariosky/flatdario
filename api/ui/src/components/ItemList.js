import React from 'react'
import {graphql} from 'react-apollo'
import gql from 'graphql-tag'
import Item from './Item'
import InfiniteScroll from 'react-infinite-scroller'
import Loader from './utils/Loader'
import Message from './utils/Message'
import injectSheet from 'react-jss'
import Fade from './Animator'

const FETCH_PAGE_SIZE = 12


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
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gridGap: '2rem',
    justifyContent: 'center',
    maxWidth: '1024px',
    padding: '0 20px', // badges are positioned off-screen: this prevents also scroll
    margin: 'auto',

    '&:after': {
      content: '',
      flex: 'auto'
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
      return <Message color="orange" text="No data"/>
    }
    if (data && data.error) {
      console.error('error:', data.error.message)
      return <Message color="tomato" text="Error getting data"/>
    }
    const items = data.items.edges
    const itemsBlock = items.map(
      (item, p) => <Fade in={true} key={item.node.id}>
        <Item item={item.node}/>
      </Fade>
    )
    const hasMore = data.items.pageInfo.hasNextPage
    return (
      <div className="clipper" style={{overflow: 'auto'}}>
        <InfiniteScroll
          loadMore={loadMore}
          hasMore={hasMore}
          loader={<Loader key={0}/>}
          useCapture={{passive: true}}
          threshold={400} // 250 is the default
          className={classes.aggregation}>
          {itemsBlock}
        </InfiniteScroll>
      </div>
    )
  }
}

const queryOptions = {
  options: (props) => {
    const query = props.match.params.query
    // map the object props to query options
    return {
      variables: {
        first: FETCH_PAGE_SIZE,
        query
      }
    }
  },
  props: ({data}) => {
    // get data from GQL response, and return object props
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
