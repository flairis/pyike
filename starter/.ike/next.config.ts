import type { NextConfig } from "next";

const withMarkdoc = require('@markdoc/next.js');

module.exports = withMarkdoc(/* options */)({
  pageExtensions: ['md', 'mdoc', 'js', 'jsx', 'ts', 'tsx']
});

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
};

export default nextConfig;
