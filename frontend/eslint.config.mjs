import globals from "globals";
import pluginReact from "eslint-plugin-react";


/** @type {import('eslint').Linter.Config[]} */
export default [
  {files: ["**/*.{js,mjs,cjs,jsx}"]},
  {languageOptions: { globals: globals.browser }},
  pluginReact.configs.flat.recommended,
];
pluginReact.configs.flat.recommended,
{
  settings: {
    react: {
      version: "detect", // Автоматически определяет версию React
    },
  },
}