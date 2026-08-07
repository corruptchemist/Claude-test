/**
 * Two flat palettes keyed by color scheme. Values follow iOS system colors so
 * the app looks native next to Apple's own apps.
 */
export type Theme = {
  background: string;
  card: string;
  border: string;
  text: string;
  textMuted: string;
  accent: string;
  danger: string;
  placeholder: string;
};

const light: Theme = {
  background: '#F2F2F7',
  card: '#FFFFFF',
  border: '#E3E3E8',
  text: '#11111C',
  textMuted: '#8A8A8E',
  accent: '#007AFF',
  danger: '#FF3B30',
  placeholder: '#B0B0B6',
};

const dark: Theme = {
  background: '#000000',
  card: '#1C1C1E',
  border: '#2C2C2E',
  text: '#FFFFFF',
  textMuted: '#98989F',
  accent: '#0A84FF',
  danger: '#FF453A',
  placeholder: '#5A5A5F',
};

/**
 * Accepts React Native's `ColorSchemeName`, which includes 'unspecified' as
 * well as null; anything that is not explicitly dark falls back to light.
 */
export function getTheme(scheme: string | null | undefined): Theme {
  return scheme === 'dark' ? dark : light;
}
