import React from 'react'
import injectSheet from 'react-jss'


const styles = {
  form: {
    maxWidth: '1024px',
    margin: '30px auto'
  },
  input: {
    width: '500px',
    maxWidth: '100%',
    display: 'block',
    padding: '10px 20px',
    margin: '15px 0',
    fontSize: '18pt',
    border: 0,
    boxSizing: 'border-box'
  },
  textarea: {},
  send: {
    backgroundColor: 'white'
  }
}

class ContactForm extends React.Component {

  render() {
    const {classes} = this.props
    return (
      <div className={classes.form}>
        <h1>Tell me what you think...</h1>
        <label>Your name: <input className={classes.input}/></label>
        <label>Your email: <input type="email" className={classes.input}/></label>
        <label>
          Your message:
          <textarea rows="3" className={[classes.input, classes.textarea].join(' ')}>
          </textarea>
        </label>

        <input type="submit" value="Send" className={[classes.input, classes.send].join(' ')}/>
      </div>
    )
  }

}

export default injectSheet(styles)(ContactForm)
