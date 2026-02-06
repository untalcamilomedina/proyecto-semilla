
import { ImageResponse } from "next/og";

// Route segment config
export const runtime = "edge";

// Image metadata
export const size = {
  width: 32,
  height: 32,
};
export const contentType = "image/png";

// Image generation
export default function Icon() {
  const color = "#ffffff"; // White

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "black",
        }}
      >
        <svg
          width="32"
          height="32"
          viewBox="0 0 512 512"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
           <path d="M120 120 H 280 V 200 H 200 V 392 H 120 V 120 Z" fill={color}/>
           <path d="M392 392 H 232 V 312 H 312 V 120 H 392 V 392 Z" fill={color}/>
           <circle cx="256" cy="256" r="40" fill={color} stroke="white" strokeWidth="20"/>
        </svg>
      </div>
    ),
    {
      ...size,
    }
  );
}
