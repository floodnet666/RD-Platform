import { expect, test } from 'vitest';
import { translations } from './translations';

test('i18n: Italian and English dictionaries should have identical keys', () => {
  const itKeys = Object.keys(translations.it).sort();
  const enKeys = Object.keys(translations.en).sort();
  
  expect(itKeys).toEqual(enKeys);
});

test('i18n: translations should not be empty', () => {
  expect(translations.it.title.length).toBeGreaterThan(0);
  expect(translations.en.title.length).toBeGreaterThan(0);
});
