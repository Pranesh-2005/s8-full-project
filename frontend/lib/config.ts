// Hugging Face Space Configuration
export const HF_SPACE_CONFIG = {
  // HF Space name
  spaceName: process.env.NEXT_PUBLIC_HF_SPACE || 'Pranesh64/s8-project',
  
  // HF Token (optional, but recommended for higher rate limits)
  hfToken: process.env.NEXT_PUBLIC_HF_TOKEN || '',
  
  // API endpoint
  endpoint: '/search_and_answer',
  
  // Default parameters
  defaultTopK: 3,
};

// Validate required environment variables
export function validateConfig(): { valid: boolean; message?: string } {
  if (!HF_SPACE_CONFIG.spaceName) {
    return {
      valid: false,
      message: 'HF_SPACE not configured. Set NEXT_PUBLIC_HF_SPACE environment variable.',
    };
  }
  return { valid: true };
}
