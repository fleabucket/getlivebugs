import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://getlivebugs.com',
  output: 'static',
  integrations: [sitemap()],
});
