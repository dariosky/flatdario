import React from 'react'
import injectSheet from 'react-jss'
import { SyncLoader } from 'react-spinners'

const styles = {
  loader: {
    margin: '2em',
    textAlign: 'center',
    gridColumn: '1/-1',
  },
}
const Loader = ({ classes }) => {
  return (
    <div className={classes.loader}>
      <SyncLoader color="#CCC" />
    </div>
  )
}

export default injectSheet(styles)(Loader)
