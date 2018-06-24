import React from 'react'
import injectSheet from 'react-jss'
import Badge from './Badge'

const styles = {
  item: {
    transition: 'all .2s ease',

    position: 'relative',
    border: '1px solid #666',
    margin: '20px 0',
    height: '220px',

    '&:hover': {
      transform: 'scale(1.1)',
      zIndex: '2'
    }
  },

  itemContent: `
    background-color: white;
    width: 100%;
  `,

  thumb: `
    height: 100%;
    width: 100%;
    background-size: contain;
    background-position: center center;
    background-repeat: no-repeat;
  `,

  title: `
    color: #eee;
    text-align: center;
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(0, 0, 0, 0.95);
    padding: 5px 5px;
  `,

  date: `
    position: absolute;
    top: 100%;
    right: 0;
    margin: 2px 0;
    text-align: right;
    font-size: 10px;
  `
}

const SubTitle = (props) => {
  const {item} = props

  if (item.type === 'Tumblr' && (item.description || item.subtitle)) {
    return <div className="subtitle">
      {item.description || item.subtitle}
    </div>
  }
  return null
}

const CardContent = injectSheet(styles)((props) => {
  const {item, classes} = props

  const backgroundStyle = () => {
    return item.thumb ? {backgroundImage: `url(${item.thumb})`} : {}
  }

  if (item.contentFormat === 'iframe') {
    return <iframe src={item.content || item.url}
                   className={classes.thumb}
                   title={item.title}
                   frameBorder="0" allowFullScreen
    />
  }
  else {
    return <div className={classes.thumb} style={backgroundStyle()}
    />
  }
})

class Item extends React.Component {
  item = () => {
    let {'extra': extraJSON, ...res} = this.props.item
    const extraObj = JSON.parse(extraJSON)
    return {...res, ...extraObj}
  }

  render() {
    const item = this.item(),
      {classes} = this.props
    return <div className={classes.item}>
      <Badge type={item.type}/>
      <a href={item.url} target="_blank" rel="noopener" className={classes.itemContent}>
        <CardContent item={item}/>
        <div className={classes.title}>
          <div className='ellipsed-text'>
            {item.title || item.url}
            <SubTitle item={item}/>
          </div>
        </div>
      </a>
      <div className={classes.date}>
        {item.timestamp}
      </div>
    </div>

  }
}

export default injectSheet(styles)(Item)
