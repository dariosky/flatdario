import React from 'react'
import injectSheet from 'react-jss'

const styles = {
  message: (props) => {
    return {
      fontSize: "16pt",
      padding: "10px",
      textAlign: "center",
      color: props.color || '#ccc'
    }
  }
}
const Message = ({text, classes}) => {
  return <div className={classes.message}>
    {text}
  </div>
}

export default injectSheet(styles)(Message)
