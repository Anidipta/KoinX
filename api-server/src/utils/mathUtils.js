/**
 * Utility functions for mathematical operations
 */

/**
 * Calculate standard deviation of an array of numbers
 * @param {number[]} values - Array of numeric values
 * @returns {number} - Standard deviation
 */
function calculateStandardDeviation(values) {
  // Calculate mean
  const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
  
  // Calculate sum of squared differences from mean
  const squaredDiffsSum = values.reduce((sum, value) => {
    const diff = value - mean;
    return sum + (diff * diff);
  }, 0);
  
  // Calculate variance and standard deviation
  const variance = squaredDiffsSum / values.length;
  const stdDev = Math.sqrt(variance);
  
  return Number(stdDev.toFixed(2));
}

module.exports = {
  calculateStandardDeviation
};