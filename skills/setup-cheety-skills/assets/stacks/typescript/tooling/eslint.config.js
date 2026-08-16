// Ergaenzt den Prinzipienpruefer um das, was ESLint besser kann.
// Die Schichtgrenzen selbst erzwingt tools/arch-check.
import ts from 'typescript-eslint';

export default ts.config(
  ...ts.configs.strictTypeChecked,
  {
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-misused-promises': 'error',
      '@typescript-eslint/switch-exhaustiveness-check': 'error',
      '@typescript-eslint/consistent-type-imports': 'error',
      'no-restricted-syntax': [
        'error',
        {
          selector: 'ExportDefaultDeclaration',
          message: 'Kein Default-Export — erschwert Umbenennen und automatische Importe.',
        },
      ],
    },
  },
);
