/**
 * From ReactGA Community Wiki Page
 * https://github.com/react-ga/react-ga/wiki/React-Router-v4-withTracker
 */

import React, {Component} from 'react'
import ReactGA from 'react-ga'
import _ from 'lodash'

const trackPage = (page) => {
  ReactGA.set({
    page
  })
  ReactGA.pageview(page)
}

const throttledTrack = _.throttle(
  trackPage,
  1500, {trailing: true, leading: false}
)

export default function withTracker(WrappedComponent) {
  return class extends Component {
    componentDidMount() {
      const page = this.props.location.pathname
      throttledTrack(page)
    }

    componentWillReceiveProps(nextProps) {
      const currentPage = this.props.location.pathname
      const nextPage = nextProps.location.pathname

      if (currentPage !== nextPage) {
        trackPage(nextPage)
      }
    }

    render() {
      return <WrappedComponent {...this.props} />
    }
  }
}
