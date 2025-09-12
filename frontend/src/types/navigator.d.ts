interface Navigator {
  connection?: {
    effectiveType: string;
    downlink: number;
    rtt: number;
  };
  mozConnection?: {
    effectiveType: string;
    downlink: number;
    rtt: number;
  };
  webkitConnection?: {
    effectiveType: string;
    downlink: number;
    rtt: number;
  };
  getBattery?: () => Promise<{
    level: number;
    charging: boolean;
  }>;
}