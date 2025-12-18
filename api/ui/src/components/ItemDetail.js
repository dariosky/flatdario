import React from 'react'
import { graphql } from 'react-apollo'
import gql from 'graphql-tag'
import injectSheet from 'react-jss'
import Loader from './utils/Loader'
import Message from './utils/Message'

const QueryItem = gql`
  query getItem($id: ID!) {
    item(id: $id) {
      id
      type
      title
      url
      timestamp
      extra
    }
  }
`

const styles = {
  wrapper: {
    minHeight: '100vh',
    backgroundColor: '#05070c',
    color: 'white',
    display: 'flex',
    flexDirection: 'column',
  },
  hero: {
    position: 'relative',
    minHeight: '260px',
    padding: '32px 18px',
    overflow: 'hidden',
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'center',
    textAlign: 'center',
  },
  heroBg: {
    position: 'absolute',
    inset: 0,
    backgroundImage:
      'linear-gradient(180deg, rgba(5,7,12,0.2) 0%, rgba(5,7,12,0.9) 65%), url(/img/coding-bkg.jpg)',
    backgroundSize: 'cover',
    backgroundPosition: '50% 50%',
    filter: 'saturate(1.1)',
  },
  logo: {
    position: 'relative',
    width: '260px',
    maxWidth: '80vw',
    marginBottom: '10px',
    filter: 'drop-shadow(0 8px 18px rgba(0,0,0,0.55))',
  },
  heroText: {
    position: 'relative',
    fontSize: '16px',
    color: '#e5e7eb',
  },
  content: {
    flex: 1,
    maxWidth: '1200px',
    margin: '0 auto',
    width: '100%',
    padding: '20px 16px 40px',
  },
  title: {
    fontSize: '28px',
    margin: '18px 0 8px',
    lineHeight: 1.3,
  },
  meta: {
    color: '#9ca3af',
    fontSize: '14px',
    marginBottom: '12px',
  },
  mediaShell: {
    position: 'relative',
    paddingTop: '56.25%',
    borderRadius: '14px',
    overflow: 'hidden',
    background: 'radial-gradient(circle at 20% 20%, #1f2937, #0b0d12)',
    boxShadow: '0 30px 60px rgba(0,0,0,0.35)',
  },
  iframe: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    border: 0,
  },
  image: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  },
  fallback: {
    display: 'grid',
    placeItems: 'center',
    color: '#e5e7eb',
    fontSize: '16px',
    position: 'absolute',
    inset: 0,
  },
  linkRow: {
    marginTop: '16px',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    flexWrap: 'wrap',
  },
  pill: {
    border: '1px solid #374151',
    borderRadius: '999px',
    padding: '6px 12px',
    color: '#e5e7eb',
    textDecoration: 'none',
    background: 'rgba(255,255,255,0.04)',
    transition: 'background .2s ease, transform .2s ease',
    '&:hover': {
      background: 'rgba(255,255,255,0.08)',
      transform: 'translateY(-1px)',
    },
  },
  description: {
    marginTop: '12px',
    color: '#d1d5db',
    lineHeight: 1.5,
    fontSize: '15px',
  },
  notFound: {
    minHeight: '60vh',
    display: 'grid',
    placeItems: 'center',
    textAlign: 'center',
    gap: '12px',
    color: '#e5e7eb',
  },
  notFoundTitle: {
    fontSize: '28px',
    margin: 0,
  },
  notFoundSub: {
    color: '#9ca3af',
    margin: 0,
  },
  ghostPill: {
    display: 'inline-block',
    marginTop: '10px',
    padding: '8px 16px',
    borderRadius: '999px',
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid #374151',
    color: '#e5e7eb',
    textDecoration: 'none',
  },
}

const parseExtra = (extra) => {
  if (!extra) return {}
  try {
    return JSON.parse(extra)
  } catch (e) {
    console.warn('Cannot parse extra', e)
    return {}
  }
}

const getEmbedUrl = (item) => {
  const url = item.url || ''
  if (/youtube\.com\/watch\?v=/.test(url)) {
    const videoId = new URL(url).searchParams.get('v')
    return videoId ? `https://www.youtube.com/embed/${videoId}` : null
  }
  if (/youtu\.be\//.test(url)) {
    const parts = url.split('/')
    const videoId = parts[parts.length - 1]
    return videoId ? `https://www.youtube.com/embed/${videoId}` : null
  }
  if (/vimeo\.com\//.test(url)) {
    const parts = url.split('/')
    const videoId = parts.pop()
    return videoId ? `https://player.vimeo.com/video/${videoId}` : null
  }
  if (item.contentFormat === 'iframe' && item.content) {
    return item.content
  }
  return null
}

const pickImage = (item) => {
  if (item.thumb) return item.thumb
  if (item.thumbnails && item.thumbnails.high) return item.thumbnails.high.url
  if (item.thumbnails && item.thumbnails.medium) return item.thumbnails.medium.url
  return null
}

const setMeta = (item) => {
  if (!item) return
  const title = item.title || 'FlatDario'
  const description =
    item.description ||
    item.subtitle ||
    'Things I liked across the web, collected by FlatDario.'
  document.title = title
  const ensure = (name, attr = 'name') => {
    let tag = document.querySelector(`meta[${attr}="${name}"]`)
    if (!tag) {
      tag = document.createElement('meta')
      tag.setAttribute(attr, name)
      document.head.appendChild(tag)
    }
    return tag
  }
  ensure('description').setAttribute('content', description)
  ensure('og:title', 'property').setAttribute('content', title)
  ensure('og:description', 'property').setAttribute('content', description)
  ensure('og:url', 'property').setAttribute('content', window.location.href)
  const image = pickImage(item)
  if (image) {
    ensure('og:image', 'property').setAttribute('content', image)
  }
}

class ItemDetail extends React.Component {
  componentDidMount() {
    this.updateMeta()
  }

  componentDidUpdate(prevProps) {
    if (this.props.data !== prevProps.data && !this.props.data.loading) {
      this.updateMeta()
    }
  }

  updateMeta() {
    const { data } = this.props
    if (!data || !data.item) return
    const item = this.mergeItem(data.item)
    setMeta(item)
  }

  mergeItem(raw) {
    const { extra: extraJSON, ...base } = raw || {}
    return { ...base, ...parseExtra(extraJSON) }
  }

  renderMedia(item, classes) {
    const embedUrl = getEmbedUrl(item)
    const image = pickImage(item)
    if (embedUrl) {
      return (
        <div className={classes.mediaShell}>
          <iframe
            src={embedUrl}
            title={item.title}
            allowFullScreen
            className={classes.iframe}
          />
        </div>
      )
    }
    if (image) {
      return (
        <div className={classes.mediaShell}>
          <img src={image} alt={item.title} className={classes.image} />
        </div>
      )
    }
    return <div className={classes.fallback}>No preview available</div>
  }

  render() {
    const { data, classes } = this.props
    if (data.loading) return <Loader />
    if (data.error) {
      console.error('Item detail error:', data.error)
      return <Message color="tomato" text="Error loading item" />
    }
    if (!data.item) {
      return (
        <div className={classes.wrapper}>
          <div className={classes.hero}>
            <div className={classes.heroBg} />
            <img
              src="/img/dariovarotto-white.svg"
              alt="Dario Varotto"
              className={classes.logo}
            />
            <div className={classes.heroText}>Dreaming Electric Sheep</div>
          </div>
          <div className={classes.notFound}>
            <h1 className={classes.notFoundTitle}>Hmm, this item drifted away.</h1>
            <p className={classes.notFoundSub}>
              It may have been removed or never existed. Try heading back to the feed.
            </p>
            <a href="/" className={classes.ghostPill}>
              Back to Home
            </a>
          </div>
        </div>
      )
    }

    const item = this.mergeItem(data.item)
    return (
      <div className={classes.wrapper}>
        <div className={classes.hero}>
          <div className={classes.heroBg} />
          <img
            src="/img/dariovarotto-white.svg"
            alt="Dario Varotto"
            className={classes.logo}
          />
          <div className={classes.heroText}>Signal from the feed</div>
        </div>
        <div className={classes.content}>
          {this.renderMedia(item, classes)}
          <h1 className={classes.title}>{item.title || 'Untitled item'}</h1>
          <div className={classes.meta}>
            {item.type || 'Item'} • {item.timestamp || 'Date unknown'}
          </div>
          {item.description || item.subtitle ? (
            <div className={classes.description}>{item.description || item.subtitle}</div>
          ) : null}
          <div className={classes.linkRow}>
            <a
              className={classes.pill}
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              Open original
            </a>
          </div>
        </div>
      </div>
    )
  }
}

const ItemDetailWithData = graphql(QueryItem, {
  options: (props) => ({
    variables: { id: props.match.params.id },
  }),
})(injectSheet(styles)(ItemDetail))

export default ItemDetailWithData
