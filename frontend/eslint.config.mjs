import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import pluginReact from "eslint-plugin-react";

export default [
  js.configs.recommended,
  {
    files: ["**/*.{js,mjs,cjs,ts,mts,cts,jsx,tsx}"],
    languageOptions: {
      globals: globals.browser
    }
  },
  ...tseslint.configs.recommended,
  pluginReact.configs.flat.recommended,
  {
    rules: {
      "react/react-in-jsx-scope": "off", // Deshabilitar para React 17+ con nuevo JSX Transform
      "@typescript-eslint/no-explicit-any": "error", // Mantener como error para forzar tipos específicos
      "@typescript-eslint/no-unused-vars": "error", // Mantener como error para variables no usadas
    }
  },
  {
    files: ["**/*.{js,mjs,cjs}"],
    languageOptions: {
      globals: {
        ...globals.node,
        module: "readonly",
        require: "readonly"
      }
    }
  }
];
