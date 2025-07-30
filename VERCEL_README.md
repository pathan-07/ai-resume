# Vercel Deployment Configuration

This project is now configured for deployment on Vercel.

## Environment Variables Required

You'll need to set these environment variables in your Vercel dashboard:

- `SECRET_KEY` - A secure random string for Flask sessions
- `GOOGLE_API_KEY` - Your Google Generative AI API key
- `SENDER_EMAIL` - Gmail address for sending emails
- `SENDER_PASSWORD` - Gmail app password for email sending

## Important Notes

1. **Database**: Uses in-memory SQLite on Vercel (data doesn't persist between requests)
2. **File Storage**: No persistent file storage on Vercel
3. **Sessions**: User sessions and data will not persist between serverless function invocations

## Deployment Steps

1. Install Vercel CLI: `npm i -g vercel`
2. Login to Vercel: `vercel login`
3. Deploy: `vercel`
4. Set environment variables in Vercel dashboard
5. Redeploy: `vercel --prod`

## Limitations on Vercel

- No persistent database (consider using external database like PlanetScale, Supabase)
- No file uploads persistence
- 30-second function timeout
- Cold starts may occur

For production use, consider:
- External database (PostgreSQL, MySQL)
- Cloud storage for file uploads (AWS S3, Cloudinary)
- Redis for session storage
