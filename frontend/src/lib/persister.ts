import type { PersistedClient } from '@tanstack/react-query-persist-client';
import { offlineStorage } from './storage';

/**
 * Custom persister for TanStack Query using Dexie (IndexedDB).
 * Allows the query cache to persist across reloads and work offline.
 */
export const dexiePersister = {
    persistClient: async (client: PersistedClient) => {
        await offlineStorage.setItem('queryCache', client);
    },
    restoreClient: async (): Promise<PersistedClient | undefined> => {
        const data = await offlineStorage.getItem<PersistedClient>('queryCache');
        return data ?? undefined;
    },
    removeClient: async () => {
        await offlineStorage.removeItem('queryCache');
    },
};
