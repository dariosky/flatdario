import React from 'react'
import injectSheet from 'react-jss'
import FontAwesomeIcon from '@fortawesome/react-fontawesome'
import {
  faGithub,
  faInstagram,
  faLinkedin,
  faTwitter,
} from '@fortawesome/fontawesome-free-brands'
import { faMusic } from '@fortawesome/fontawesome-free-solid'

const styles = {
  block: {
    maxWidth: '1100px',
    margin: '30px auto',
    padding: '20px',
  },
  hero: {
    background: 'linear-gradient(135deg, #f7f9fb, #eef2f7)',
    borderRadius: '16px',
    padding: '32px',
    boxShadow: '0 20px 45px rgba(45, 55, 72, 0.12)',
    marginBottom: '26px',
  },
  heroTitle: {
    margin: '0 0 10px',
    fontSize: '28px',
    fontWeight: 700,
    color: '#1f2937',
  },
  heroSubtitle: {
    margin: 0,
    color: '#4b5563',
    fontSize: '15px',
    lineHeight: 1.5,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gridGap: '18px',
  },
  link: {
    textDecoration: 'none',
    color: 'inherit',
  },
  card: {
    background: '#fff',
    borderRadius: '14px',
    padding: '18px 16px',
    border: '1px solid #e5e7eb',
    boxShadow: '0 10px 24px rgba(17, 24, 39, 0.08)',
    transition: 'transform .2s ease, box-shadow .2s ease',
    '&:hover': {
      transform: 'translateY(-3px)',
      boxShadow: '0 16px 28px rgba(17, 24, 39, 0.12)',
    },
  },
  titleRow: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '8px',
  },
  icon: {
    width: '22px',
    height: '22px',
    marginRight: '10px',
    color: '#111827',
  },
  name: {
    fontSize: '16px',
    fontWeight: 700,
    color: '#111827',
    margin: 0,
  },
  desc: {
    margin: 0,
    color: '#4b5563',
    fontSize: '14px',
    lineHeight: 1.5,
  },
  tag: {
    marginTop: '6px',
    fontSize: '12px',
    color: '#6b7280',
  },
}

class Contacts extends React.Component {
  render() {
    const { classes } = this.props
    const links = [
      {
        name: 'GitHub',
        url: 'https://github.com/dariosky',
        icon: faGithub,
        desc: 'Open source projects, experiments, and code snippets.',
      },
      {
        name: 'LinkedIn',
        url: 'https://www.linkedin.com/in/dariovarotto/',
        icon: faLinkedin,
        desc: 'Work updates, collaborations, and professional threads.',
      },
      {
        name: 'Instagram',
        url: 'https://www.instagram.com/dariosky/',
        icon: faInstagram,
        desc: 'Visual notes from travels, hobbies, and daily snapshots.',
      },
      {
        name: 'Twitter',
        url: 'https://twitter.com/dariosky',
        icon: faTwitter,
        desc: 'Quick thoughts, experiments, and tech chatter.',
      },
      {
        name: 'Lykd',
        url: 'https://lykd.it',
        icon: faMusic,
        desc: 'Side project for music lovers — your likes made social.',
      },
    ]

    return (
      <div className={classes.block}>
        <div className={classes.hero}>
          <h1 className={classes.heroTitle}>Let’s connect</h1>
          <p className={classes.heroSubtitle}>
            I’m Dario Varotto, currently creating from Marbella, Spain. Ping me on any
            channel below — I’m always up for music, code, and product ideas.
          </p>
        </div>

        <div className={classes.grid}>
          {links.map((link) => (
            <a
              className={classes.link}
              href={link.url}
              key={link.name}
              target="_blank"
              rel="noopener noreferrer"
            >
              <div className={classes.card}>
                <div className={classes.titleRow}>
                  <FontAwesomeIcon icon={link.icon} className={classes.icon} />
                  <p className={classes.name}>{link.name}</p>
                </div>
                <p className={classes.desc}>{link.desc}</p>
                <div className={classes.tag}>Open in new tab</div>
              </div>
            </a>
          ))}
        </div>
      </div>
    )
  }
}

export default injectSheet(styles)(Contacts)
