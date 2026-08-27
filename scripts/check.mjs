import { writeFileSync, readFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const dataPath = join(__dirname, '..', 'data.json');

const HISTORY_LIMIT = 288;
const TIMEOUT_MS = 10000;
const DEGRADED_MS = 3000;

const services = [
    { id: 'soundcloud', name: 'SoundCloud API', url: 'https://api-v2.soundcloud.com/' },
    { id: 'lyrics', name: 'Lyrics API (lrclib.net)', url: 'https://lrclib.net/api/search?track_name=test&artist_name=test' },
    { id: 'kugou', name: 'Kugou API', url: 'https://songsearch.kugou.com/song_search_v2?keyword=test&page=1&pagesize=10&userid=-1&clientver=&platform=WebFilter&filter=2&iscorrection=1&privilege_filter=0' },
];

async function checkService(service) {
    const start = Date.now();
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);
        const res = await fetch(service.url, {
            signal: controller.signal,
            headers: { 'User-Agent': 'resona-status-bot/1.0' },
        });
        clearTimeout(timeout);
        const latency = Date.now() - start;
        let status = 'operational';
        if (res.status >= 500) status = 'down';
        else if (latency > DEGRADED_MS) status = 'degraded';
        return { status, latency_ms: latency, http_status: res.status };
    } catch {
        const latency = Date.now() - start;
        return { status: 'down', latency_ms: latency, http_status: 0 };
    }
}

function loadData() {
    if (!existsSync(dataPath)) return { generated_at: null, services: [] };
    try {
        return JSON.parse(readFileSync(dataPath, 'utf-8'));
    } catch {
        return { generated_at: null, services: [] };
    }
}

async function main() {
    const existingData = loadData();
    const now = new Date().toISOString();
    const results = [];

    for (const service of services) {
        const existing = existingData.services.find(s => s.id === service.id);
        const check = await checkService(service);
        const history = [...(existing?.history || []), { t: now, status: check.status, latency_ms: check.latency_ms }].slice(-HISTORY_LIMIT);
        results.push({
            id: service.id,
            name: service.name,
            url: service.url,
            status: check.status,
            http_status: check.http_status,
            latency_ms: check.latency_ms,
            checked_at: now,
            history,
        });
    }

    writeFileSync(dataPath, JSON.stringify({ generated_at: now, services: results }, null, 2) + '\n');
}

main();
