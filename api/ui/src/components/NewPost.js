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
    maxWidth: '520px',
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
  progressTrack: {
    height: '6px',
    borderRadius: '999px',
    background: 'rgba(255,255,255,0.08)',
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    width: '40%',
    borderRadius: '999px',
    background:
      'linear-gradient(90deg, rgba(34,211,238,0.9), rgba(99,102,241,0.9), rgba(168,85,247,0.9))',
    animation: '$indeterminate 1.1s ease-in-out infinite',
  },
  '@keyframes indeterminate': {
    '0%': { transform: 'translateX(-100%)' },
    '50%': { transform: 'translateX(40%)' },
    '100%': { transform: 'translateX(140%)' },
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

class NewPost extends React.Component {
  state = { url: '', message: '', success: false, isAdmin: false, loading: false }

  async componentDidMount() {
    try {
      const res = await fetch(`${config.API_BASE}auth/me`, { credentials: 'include' })
      const data = await res.json()
      this.setState({ isAdmin: !!data.authenticated })
    } catch (e) {
      this.setState({ isAdmin: false })
    }
  }

  handleChange = (e) => {
    this.setState({ url: e.target.value })
  }

  submit = async (e) => {
    e.preventDefault()
    const { url } = this.state
    if (!url) {
      this.setState({ message: 'Please enter a URL', success: false })
      return
    }
    try {
      this.setState({ loading: true, message: '' })
      const res = await fetch(`${config.API_BASE}admin/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ url }),
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.error || 'Create failed')
      }
      this.setState({ message: 'Post created', success: true })
      window.dispatchEvent(new Event('items:refresh'))
      setTimeout(() => this.props.history.push(`/view/${data.id}`), 400)
    } catch (err) {
      this.setState({ message: err.message, success: false })
    } finally {
      this.setState({ loading: false })
    }
  }

  render() {
    const { classes } = this.props
    const { url, message, success, isAdmin, loading } = this.state
    if (!isAdmin) {
      return (
        <div className={classes.page}>
          <div className={classes.card}>
            <h1 className={classes.title}>Admin only</h1>
            <p className={classes.subtitle}>Please login to create a new post.</p>
          </div>
        </div>
      )
    }
    return (
      <div className={classes.page}>
        <div className={classes.card}>
          <h1 className={classes.title}>New post</h1>
          <p className={classes.subtitle}>Paste a URL to add a new item.</p>
          <form className={classes.form} onSubmit={this.submit}>
            <label className={classes.label}>
              URL
              <input
                className={classes.input}
                name="url"
                value={url}
                onChange={this.handleChange}
                placeholder="https://www.youtube.com/watch?v=..."
                disabled={loading}
              />
            </label>
            <button className={classes.button} type="submit">
              {loading ? 'Creating...' : 'Create'}
            </button>
            {loading ? (
              <div className={classes.progressTrack}>
                <div className={classes.progressBar} />
              </div>
            ) : null}
            {message ? (
              <div className={success ? classes.success : classes.error}>{message}</div>
            ) : null}
          </form>
        </div>
      </div>
    )
  }
}

export default injectSheet(styles)(NewPost)
