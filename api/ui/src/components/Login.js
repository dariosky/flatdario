import React from 'react'
import injectSheet from 'react-jss'
import config from '../util/config'

const styles = {
  page: {
    minHeight: '100vh',
    display: 'grid',
    placeItems: 'center',
    background: 'radial-gradient(circle at 20% 20%, #0f172a, #0b1020 60%)',
    color: '#e5e7eb',
    padding: '20px',
  },
  card: {
    width: '100%',
    maxWidth: '420px',
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: '16px',
    padding: '26px',
    boxShadow: '0 30px 60px rgba(0,0,0,0.35)',
    backdropFilter: 'blur(6px)',
  },
  title: {
    margin: '0 0 6px',
    fontSize: '26px',
  },
  subtitle: {
    margin: 0,
    color: '#9ca3af',
    fontSize: '14px',
  },
  form: {
    marginTop: '18px',
    display: 'grid',
    gap: '14px',
  },
  label: {
    display: 'flex',
    flexDirection: 'column',
    fontSize: '14px',
    color: '#cbd5e1',
  },
  input: {
    marginTop: '6px',
    padding: '10px 12px',
    borderRadius: '10px',
    border: '1px solid #334155',
    background: '#0b1220',
    color: 'white',
    fontSize: '15px',
  },
  passwordRow: {
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
  },
  toggle: {
    position: 'absolute',
    right: '10px',
    top: '36px',
    border: 'none',
    background: 'transparent',
    color: '#a5b4fc',
    cursor: 'pointer',
    fontSize: '12px',
    padding: 0,
  },
  button: {
    marginTop: '6px',
    padding: '12px 14px',
    borderRadius: '10px',
    border: 'none',
    background: 'linear-gradient(120deg, #22d3ee 0%, #6366f1 50%, #a855f7 100%)',
    color: 'white',
    fontSize: '15px',
    cursor: 'pointer',
    transition: 'transform .15s ease, box-shadow .15s ease',
    boxShadow: '0 12px 30px rgba(99,102,241,0.35)',
    '&:hover': {
      transform: 'translateY(-1px)',
      boxShadow: '0 16px 36px rgba(99,102,241,0.45)',
    },
  },
  error: {
    color: '#f87171',
    fontSize: '14px',
  },
  success: {
    color: '#34d399',
    fontSize: '14px',
  },
}

class Login extends React.Component {
  state = { username: '', password: '', message: '', success: false, showPass: false }

  handleChange = (e) => {
    this.setState({ [e.target.name]: e.target.value })
  }

  submit = async (e) => {
    e.preventDefault()
    const { username, password } = this.state
    if (!username || !password) {
      this.setState({ message: 'Please enter username and password', success: false })
      return
    }
    try {
      const res = await fetch(`${config.API_BASE}auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.error || 'Login failed')
      }
      this.setState({ message: 'Logged in', success: true })
      setTimeout(() => this.props.history.push('/'), 300)
    } catch (err) {
      this.setState({ message: err.message, success: false })
    }
  }

  render() {
    const { classes } = this.props
    const { username, password, message, success } = this.state
    return (
      <div className={classes.page}>
        <div className={classes.card}>
          <h1 className={classes.title}>Admin login</h1>
          <p className={classes.subtitle}>Enter credentials to manage posts.</p>
          <form className={classes.form} onSubmit={this.submit}>
            <label className={classes.label}>
              Username
              <input
                className={classes.input}
                name="username"
                value={username}
                onChange={this.handleChange}
                autoComplete="username"
              />
            </label>
            <label className={`${classes.label} ${classes.passwordRow}`}>
              Password
              <input
                className={classes.input}
                type={this.state.showPass ? 'text' : 'password'}
                name="password"
                value={password}
                onChange={this.handleChange}
                autoComplete="current-password"
              />
              <button
                type="button"
                className={classes.toggle}
                onClick={() => this.setState({ showPass: !this.state.showPass })}
              >
                {this.state.showPass ? 'Hide' : 'Show'}
              </button>
            </label>
            <button className={classes.button} type="submit">
              Login
            </button>
            {message ? (
              <div className={success ? classes.success : classes.error}>{message}</div>
            ) : null}
          </form>
        </div>
      </div>
    )
  }
}

export default injectSheet(styles)(Login)
