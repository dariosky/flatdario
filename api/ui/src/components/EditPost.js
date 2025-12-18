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
    maxWidth: '700px',
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
  textarea: {
    marginTop: '6px',
    minHeight: '200px',
    padding: '12px',
    borderRadius: '10px',
    border: '1px solid #334155',
    background: '#0b1220',
    color: 'white',
    fontSize: '13px',
    fontFamily:
      'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
  },
  buttonRow: {
    display: 'flex',
    gap: '10px',
    flexWrap: 'wrap',
  },
  button: {
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
  ghost: {
    padding: '12px 14px',
    borderRadius: '10px',
    border: '1px solid #334155',
    background: 'transparent',
    color: '#e5e7eb',
    fontSize: '15px',
    cursor: 'pointer',
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

class EditPost extends React.Component {
  state = {
    title: '',
    url: '',
    extra: '{}',
    message: '',
    success: false,
    isAdmin: false,
    loading: true,
  }

  async componentDidMount() {
    await this.checkAuth()
    if (this.state.isAdmin) {
      this.fetchItem()
    }
  }

  async checkAuth() {
    try {
      const res = await fetch(`${config.API_BASE}auth/me`, { credentials: 'include' })
      const data = await res.json()
      this.setState({ isAdmin: !!data.authenticated })
    } catch (e) {
      this.setState({ isAdmin: false, loading: false })
    }
  }

  async fetchItem() {
    try {
      const res = await fetch(
        `${config.API_BASE}admin/items/${this.props.match.params.id}`,
        {
          credentials: 'include',
        }
      )
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.error || 'Failed to load item')
      }
      const extraPretty = this.prettyJson(data.extra)
      this.setState({
        title: data.title || '',
        url: data.url || '',
        extra: extraPretty,
        loading: false,
      })
    } catch (err) {
      this.setState({ message: err.message, success: false, loading: false })
    }
  }

  prettyJson(raw) {
    try {
      const obj = typeof raw === 'string' ? JSON.parse(raw) : raw
      return JSON.stringify(obj, null, 2)
    } catch (e) {
      return typeof raw === 'string' ? raw : '{}'
    }
  }

  handleChange = (e) => {
    this.setState({ [e.target.name]: e.target.value })
  }

  submit = async (e) => {
    e.preventDefault()
    const { title, url, extra } = this.state
    try {
      JSON.parse(extra)
    } catch (e) {
      this.setState({ message: 'Extra must be valid JSON', success: false })
      return
    }
    try {
      const res = await fetch(
        `${config.API_BASE}admin/items/${this.props.match.params.id}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ title, url, extra }),
        }
      )
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.error || 'Update failed')
      }
      window.dispatchEvent(new Event('items:refresh'))
      this.setState({ message: 'Saved', success: true })
      setTimeout(
        () => this.props.history.push(`/view/${this.props.match.params.id}`),
        400
      )
    } catch (err) {
      this.setState({ message: err.message, success: false })
    }
  }

  render() {
    const { classes } = this.props
    const { title, url, extra, message, success, isAdmin, loading } = this.state
    if (!isAdmin) {
      return (
        <div className={classes.page}>
          <div className={classes.card}>
            <h1 className={classes.title}>Admin only</h1>
            <p className={classes.subtitle}>Please login to edit items.</p>
          </div>
        </div>
      )
    }
    return (
      <div className={classes.page}>
        <div className={classes.card}>
          <h1 className={classes.title}>Edit post</h1>
          <p className={classes.subtitle}>Update title, URL, or extra JSON.</p>
          <form className={classes.form} onSubmit={this.submit}>
            <label className={classes.label}>
              Title
              <input
                className={classes.input}
                name="title"
                value={title}
                onChange={this.handleChange}
                disabled={loading}
              />
            </label>
            <label className={classes.label}>
              URL
              <input
                className={classes.input}
                name="url"
                value={url}
                onChange={this.handleChange}
                disabled={loading}
              />
            </label>
            <label className={classes.label}>
              Extra (JSON)
              <textarea
                className={classes.textarea}
                name="extra"
                value={extra}
                onChange={this.handleChange}
                disabled={loading}
              />
            </label>
            <div className={classes.buttonRow}>
              <button className={classes.button} type="submit" disabled={loading}>
                Save
              </button>
              <button
                className={classes.ghost}
                type="button"
                onClick={() =>
                  this.props.history.push(`/view/${this.props.match.params.id}`)
                }
              >
                Cancel
              </button>
            </div>
            {message ? (
              <div className={success ? classes.success : classes.error}>{message}</div>
            ) : null}
          </form>
        </div>
      </div>
    )
  }
}

export default injectSheet(styles)(EditPost)
