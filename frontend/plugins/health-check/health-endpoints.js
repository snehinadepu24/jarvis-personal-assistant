// health-endpoints.js
// API endpoints for health checks and monitoring

const os = require('os');

const SERVER_START_TIME = Date.now();

/**
 * Setup health check endpoints on the dev server
 * @param {Object} devServer - Webpack dev server instance
 * @param {Object} healthPlugin - Instance of WebpackHealthPlugin
 */
function setupHealthEndpoints(devServer, healthPlugin) {
  if (!devServer || !devServer.app) {
    console.warn('[Health Check] Dev server not available, skipping health endpoints');
    return;
  }

  if (!healthPlugin) {
    console.warn('[Health Check] Health plugin not provided, skipping health endpoints');
    return;
  }

  console.log('[Health Check] Setting up health endpoints...');

  // ====================================================================