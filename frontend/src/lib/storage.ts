import Dexie, { type Table } from 'dexie';

/**
 * Offline storage using IndexedDB via Dexie.
 *
 * Note: Client-side "encryption" with a key embedded in the bundle provides
 * no real confidentiality against XSS or browser extensions. Instead of
 * false security theater, we store data as plain JSON and rely on:
 *   1. HttpOnly session cookies (not accessible to JS)
 *   2. CSP headers to prevent XSS
 *   3. Not storing sensitive data (tokens, passwords) client-side
 *
 * If encryption is truly needed, use the Web Crypto API with a key derived
 * from user credentials via PBKDF2, stored only in memory.
 */

export interface CachedItem {
  id?: number;
  key: string;
  value: string;
  timestamp: number;
}

export class OfflineStorage extends Dexie {
  items!: Table<CachedItem>;

  constructor() {
    super('OfflineDB');
    this.version(2).stores({
      items: '++id, key',
    });
  }

  async setItem(key: string, value: unknown) {
    const serialized = JSON.stringify(value);
    const existing = await this.items.where('key').equals(key).first();
    if (existing) {
      await this.items.update(existing.id!, {
        value: serialized,
        timestamp: Date.now(),
      });
    } else {
      await this.items.add({
        key,
        value: serialized,
        timestamp: Date.now(),
      });
    }
  }

  async getItem<T = unknown>(key: string): Promise<T | null> {
    const item = await this.items.where('key').equals(key).first();
    if (!item) return null;
    try {
      return JSON.parse(item.value) as T;
    } catch {
      return null;
    }
  }

  async removeItem(key: string) {
    await this.items.where('key').equals(key).delete();
  }

  async clear() {
    await this.items.clear();
  }
}

export const offlineStorage = new OfflineStorage();
