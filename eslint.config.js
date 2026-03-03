import js from "@eslint/js";

export default [
  js.configs.recommended,
  {
    rules: {
      "no-unused-vars": "warn",
      "no-undef": "error",
      "no-const-assign": "error",
      "no-empty": "error",
      "no-useless-assignment": "error"
    },
    languageOptions: {
      globals: {
        // Browser globals
        "console": "readonly",
        "fetch": "readonly",
        "setTimeout": "readonly",
        "clearTimeout": "readonly",
        "setInterval": "readonly",
        "clearInterval": "readonly",
        "localStorage": "readonly",
        "sessionStorage": "readonly",
        "window": "readonly",
        "document": "readonly",
        "XMLHttpRequest": "readonly",
        "FormData": "readonly",
        "Headers": "readonly",
        "Request": "readonly",
        "Response": "readonly",
        "Promise": "readonly",
        "URL": "readonly",
        "URLSearchParams": "readonly",
        "JSON": "readonly",
        "Math": "readonly",
        "Date": "readonly",
        "Array": "readonly",
        "Object": "readonly",
        "String": "readonly",
        "Number": "readonly",
        "Boolean": "readonly",
        "Map": "readonly",
        "Set": "readonly",
        "Symbol": "readonly",
        "Error": "readonly",
        "TypeError": "readonly",
        "RangeError": "readonly",
        "SyntaxError": "readonly",
        "encodeURIComponent": "readonly",
        "decodeURIComponent": "readonly",
        "isNaN": "readonly",
        "isFinite": "readonly",
        "parseInt": "readonly",
        "parseFloat": "readonly",
        "Infinity": "readonly",
        "NaN": "readonly",
        "undefined": "readonly",
        // Node.js globals for compatibility
        "require": "readonly",
        "module": "readonly",
        "exports": "readonly",
        "global": "readonly",
        "process": "readonly",
        "__dirname": "readonly",
        "__filename": "readonly",
        "Buffer": "readonly"
      }
    }
  }
];
