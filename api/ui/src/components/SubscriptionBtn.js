import React from 'react';
import injectStyles from 'react-jss';
import {faRssSquare} from '@fortawesome/fontawesome-free-solid'
import FontAwesomeIcon from '@fortawesome/react-fontawesome'
import {
  askPermission,
  isSubscribeAvailable,
  isSubscribed,
  subscribeUser,
  unsubscribeUser
} from '../util/pushNotifications'
import PropTypes from 'prop-types';
import axios from 'axios'
import config from '../util/config'

const styles = {
  btn: `
    backgroundColor: orange;
    color: white;
    padding: 5px 10px;
    margin: auto;
    margin-right:0;
    border-radius: 3px;
    border: 0;
    cursor: pointer;
    font-size: 13px;
  `,
  error: `
    backgroundColor: red;
  `,
  subscribed: `
    backgroundColor: #BFFFAE;
    color: black;  
  `,
  icon: `
    margin-left: 5px;
  `
};

class SubscriptionBtn extends React.Component {
  state = {
    error: null,
    subscribed: false,
    visible: false
  }

  componentDidMount() {
    this.componentWillReceiveProps(this.props);
  }

  componentWillReceiveProps(newProps) {

    this.setState({
      visible: false
    })
    isSubscribed().then((result) => {
      console.log('subscribed?', result)
      this.setState({
        subscribed: result,
        visible: isSubscribeAvailable()
      })
    })
  }

  componentDidCatch(error, info) {
    console.error(error, info)
  }

  triggerError = (error) => {
    const button = this
    console.error(error)
    button.setState({error})

    function resetError() {
      button.setState({error: null})
    }

    setTimeout(resetError, 5000)
  }

  subscribe = () => {
    const {applicationServerKey} = this.props
    askPermission().then(() => {
      console.log('Push accepted')
      subscribeUser({applicationServerKey})
        .then(subscription => {
          if (subscription)
            axios.post(config.PUSH_SUBSCRIBE_ENDPOINT, subscription)
        })
        .then(() => {
          this.setState({subscribed: true})
        })
        .catch(error => {
          this.triggerError(error)
        })
    }).catch(error => {
      alert('You cannot subscribe if you do not accept.')
    })
  }

  unsubscribe = () => {
    unsubscribeUser().then(
      (subscription) => {
        axios.post(config.PUSH_UNSUBSCRIBE_ENDPOINT, subscription)
      }
    )
      .then(() => {
        this.setState({subscribed: false})
      })
      .catch(error => {
        this.triggerError(error)
      })
  }


  render() {
    const {classes} = this.props,
      {error, visible, subscribed} = this.state
    if (error) {
      return <div className={[classes.btn, classes.error].join(' ')}>
        Cannot subscribe
      </div>
    }

    if (subscribed) {
      return (
        <button className={[classes.btn, classes.subscribed].join(' ')}
                onClick={this.unsubscribe}
        >
          Subscribed
          <FontAwesomeIcon className={classes.icon}
                           icon={faRssSquare}
          />
        </button>
      )
    }

    return visible && (
      <button className={classes.btn}
              onClick={this.subscribe}>
        Subscribe
        <FontAwesomeIcon className={classes.icon}
                         icon={faRssSquare}
        />
      </button>
    );
  }
}

SubscriptionBtn.propTypes = {
  applicationServerKey: PropTypes.string.isRequired
}

const styledSubscriptionBtn = injectStyles(styles)(SubscriptionBtn);

export default styledSubscriptionBtn;
