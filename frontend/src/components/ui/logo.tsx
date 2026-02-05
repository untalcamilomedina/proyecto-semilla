import React from "react";

export function BlockFlowLogo({ className = "w-8 h-8", color = "currentColor" }: { className?: string; color?: string }) {
  return (
    <svg 
      viewBox="0 0 512 512" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path d="M120 120 H 280 V 200 H 200 V 392 H 120 V 120 Z" fill={color}/>
      <path d="M392 392 H 232 V 312 H 312 V 120 H 392 V 392 Z" fill={color}/>
      <circle cx="256" cy="256" r="40" fill={color} stroke="white" strokeWidth="8"/>
    </svg>
  );
}
