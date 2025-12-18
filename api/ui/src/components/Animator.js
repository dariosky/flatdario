import React from 'react'
import Transition from 'react-transition-group/Transition'

const duration = 200

const defaultStyle = {
  transition: `opacity ${duration}ms ease-in-out`,
  opacity: 0,
}

const transitionStyles = {
  entering: { opacity: 0 },
  entered: { opacity: 1 },
}

const Fade = ({ in: inProp, children, delay }) => (
  <Transition in={inProp} appear={true} timeout={duration}>
    {(state) => (
      <div
        style={{
          animationDelay: delay,
          ...defaultStyle,
          ...transitionStyles[state],
        }}
      >
        {delay}
        {children}
      </div>
    )}
  </Transition>
)

export default Fade
