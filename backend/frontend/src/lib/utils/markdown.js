import { marked } from 'marked';
import DOMPurify from 'dompurify';

// Configure marked options
marked.setOptions({
  breaks: true, // Add line breaks on single line breaks
  gfm: true, // Use GitHub Flavored Markdown
  headerIds: false, // Don't add IDs to headers (for security)
  mangle: false, // Don't mangle email addresses
  sanitize: false, // Don't sanitize (we'll handle this with DOMPurify)
});

/**
 * Renders markdown to HTML with security considerations
 * @param {string} markdown - The markdown string to render
 * @returns {string} - The rendered HTML
 */
export function renderMarkdown(markdown) {
  if (!markdown) return '';

  try {
    // Convert markdown to HTML
    const html = marked.parse(markdown);

    // Sanitize the HTML to prevent XSS attacks
    const sanitizedHtml = DOMPurify.sanitize(html, {
      USE_PROFILES: { html: true },
      ALLOWED_TAGS: [
        'a',
        'b',
        'blockquote',
        'br',
        'code',
        'div',
        'em',
        'h1',
        'h2',
        'h3',
        'h4',
        'h5',
        'h6',
        'hr',
        'i',
        'li',
        'ol',
        'p',
        'pre',
        'span',
        'strong',
        'table',
        'tbody',
        'td',
        'th',
        'thead',
        'tr',
        'ul',
      ],
      ALLOWED_ATTR: ['href', 'target', 'rel', 'class'],
    });

    // Return the sanitized HTML
    return sanitizedHtml;
  } catch (error) {
    console.error('Error rendering markdown:', error);
    return markdown; // Return original text if rendering fails
  }
}
