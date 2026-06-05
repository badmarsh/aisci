import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  devIndicators: {
    appIsrStatus: false,
  },
  // @ts-ignore
  allowedDevOrigins: ["localhost:3100", "[::1]:3100", "127.0.0.1:3100", "[::1]"],
};

export default nextConfig;
