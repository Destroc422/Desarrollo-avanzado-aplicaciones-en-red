import { API_BASE_URL } from '../api/http';

const fallbackSvg = encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 560"><rect width="800" height="560" fill="#ecfccb"/><path d="M400 105l125 170-75 170H350l-75-170z" fill="#4d7c0f" opacity=".9"/><path d="M335 205h130l-65 175z" fill="#bef264"/><circle cx="510" cy="185" r="30" fill="#fef08a"/><text x="400" y="510" font-family="Arial, sans-serif" font-size="34" text-anchor="middle" fill="#365314">GrilloCocktails</text></svg>',
);

export const FALLBACK_COCKTAIL_IMAGE = `data:image/svg+xml;charset=UTF-8,${fallbackSvg}`;

const isAbsoluteUrl = (value) => /^(https?:|data:|blob:)/i.test(value);

export function resolveImageUrl(imagePath) {
  if (!imagePath) return FALLBACK_COCKTAIL_IMAGE;
  if (isAbsoluteUrl(imagePath)) return imagePath;

  const normalizedPath = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;

  try {
    const apiOrigin = new URL(API_BASE_URL, window.location.origin).origin;
    return new URL(normalizedPath, `${apiOrigin}/`).toString();
  } catch {
    return `${API_BASE_URL}${normalizedPath}`;
  }
}
