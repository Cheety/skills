export const config = {
  fristTage: 14,
  datenbankUrl: process.env.DATABASE_URL ?? '',
  mailAbsender: process.env.MAIL_FROM ?? 'noreply@example.com',
} as const;
