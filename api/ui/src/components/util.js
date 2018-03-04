import React from 'react'
import styles from '../../styles/social.scss'
import {SyncLoader} from 'react-spinners'

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
    <SyncLoader/>
  </div>
}

export {Footer, Message, Loader, LoadMoreBtn}
