import React from "react"
import {graphql} from 'react-apollo'
import gql from 'graphql-tag'
import Item from './Item'
import styles from '../../styles/social.scss'
import {SyncLoader} from 'react-spinners'

const QueryItems = gql`
query getItems($cursor: String) {
  items(first: 30, sort: TIMESTAMP_DESC, after: $cursor) {
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

class ItemList extends React.Component {
  loadMore = () => {
    console.log("Loading more")
  }

  render() {
    const {data} = this.props

    if (data.loading) {
      return <div className={styles.loader}>
        <SyncLoader
          color={'#777'}
        />
      </div>
    }
    if (!data) {
      return <Message text="No data"/>
    }
    console.log("We have data:", data)
    if (data && data.error) {
      return <div>Error</div>
    }
    const items = data.items.edges
    const itemsBlock = items.map(
      item => <Item key={item.node.id} item={item.node}/>
    )
    return [
      <div className={styles.aggregation}>
        {itemsBlock}
      </div>,
      <LoadMoreBtn onClick={data.fetchMore}/>,
      <Footer/>
    ]
  }
}

const ItemData = graphql(QueryItems,
  /*  {
      props({data: {loading, data, fetchMore}}) {
        console.log(`itemData: data: ${data}, loading: ${loading}`)
        return {
          loading,
          data,
          loadNextPage() {
            console.log("next page data:", data)
            return fetchMore({
              variables: {
                cursor: null,
              },

              updateQuery: (previousResult, {fetchMoreResult}) => {
                if (!fetchMoreResult) {
                  return previousResult
                }
                const items = fetchMoreResult.items.edges

                return [...previousResult, ...items]

              },
            })
          },
        }
      },
    }*/)(ItemList)

export default ItemData
