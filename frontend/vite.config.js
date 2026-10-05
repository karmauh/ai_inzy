import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Recharts (z d3 i lodash) to ok. 580 kB – świadomie jeden duży plik, ładowany dopiero
    // przy pierwszych wynikach analizy (React.lazy w Dashboard), więc nie spowalnia ekranu startowego
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        // Biblioteki w osobnych plikach: zmieniają się rzadziej niż kod aplikacji, więc przeglądarka
        // może je trzymać w pamięci podręcznej między aktualizacjami
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined;
          if (/node_modules\/(recharts|d3-|victory-vendor|lodash|react-smooth|recharts-scale|decimal\.js-light)/.test(id)) return 'recharts';
          if (/node_modules\/(react|react-dom|scheduler)\//.test(id)) return 'react';
          return 'vendor';
        },
      },
    },
  },
  server: {
    host: true, // Expose to all IPs (0.0.0.0) for Docker
    port: 5173,
    watch: {
        usePolling: true
    }
  }
})
