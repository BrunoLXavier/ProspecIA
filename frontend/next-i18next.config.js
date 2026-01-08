const path = require('path')

const config = {
  i18n: {
    defaultLocale: 'pt-BR',
    locales: ['pt-BR', 'en-US', 'es-ES'],
  },
  ns: ['common', 'ingestao', 'fomento', 'portfolio', 'crm', 'pipeline', 'admin'],
  defaultNS: 'common',
  fallbackLng: 'pt-BR',
  fallbackNS: 'common',
  localePath: path.resolve('./public/locales'),
  nsSeparator: '.',
  keySeparator: '.',
  interpolation: {
    escapeValue: false,
  },
}

module.exports = config
