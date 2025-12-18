const rewireReactHotLoader = require('react-app-rewire-hot-loader')
const rewireWebpackBundleAnalyzer = require('react-app-rewire-webpack-bundle-analyzer')
const {
  rewireWorkboxInject,
  defaultInjectConfig,
  rewireWorkboxGenerate,
  defaultGenerateConfig,
} = require('react-app-rewire-workbox')
const path = require('path')

/* config-overrides.js */
module.exports = function override(config, env) {
  config = rewireReactHotLoader(config, env) // hot-loader

  if (env === 'production') {
    // webpack bundle analyzer
    /* config = rewireWebpackBundleAnalyzer(config, env, {
       analyzerMode: 'static',
       reportFilename: 'report.html'
     })*/

    // workbox service adding custom Service-worker
    // the basic workbox config is like this:
    // config = rewireWorkboxGenerate()(config, env);
    // but we use a custom one
    const workboxConfig = {
      ...defaultInjectConfig,
      swSrc: path.join(__dirname, 'src', 'custom-service-worker.js'),
    }
    config = rewireWorkboxInject(workboxConfig)(config, env)
  }
  return config
}
