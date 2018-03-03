import React from "react"
import {graphql} from 'react-apollo'
import gql from 'graphql-tag'
import Item from './Item'
import styles from '../../styles/social.scss'
import {SyncLoader} from 'react-spinners'

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

const Message = ({text}) => {
  return <div className={styles.message}>
    {text}
  </div>
}

const Loader = () => {
  return <div className={styles.loader}>
    <SyncLoader
      color={'#777'}
    />
  </div>
}

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
    return <div>
      <div className={styles.aggregation}>
        {itemsBlock}
      </div>
      {data.items.pageInfo.hasNextPage &&
      <LoadMoreBtn onClick={loadMore}/>}
      <Footer/>
    </div>
  }
}

const queryOptions = {
  options: (props) => {
    return {
      variables: {first: 10}
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
