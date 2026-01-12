import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';
import { offlineStorage } from './storage';

/**
 * Custom persister for TanStack Query using Dexie (IndexedDB) with encryption.
 * This allows the query cache to persist across reloads and work offline.
 */
export const dexiePersister = {
    persistClient: async (client: any) => {
        await offlineStorage.setItem('queryCache', client);
    },
    restoreClient: async () => {
        return await offlineStorage.getItem('queryCache');
    },
    removeClient: async () => {
        await offlineStorage.removeItem('queryCache');
    }
};
