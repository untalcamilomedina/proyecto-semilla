import Dexie, { type Table } from 'dexie';
import CryptoJS from 'crypto-js';

const DEFAULT_KEY = "seed-insecure-fallback";

/**
 * Gets the encryption key for the current user.
 * In a real scenario, this would be derived from the user's login session
 * or a PBKDF2 derivative of their password stored only in memory.
 */
function getEncryptionKey(): string {
  // Attempt to get user ID from a cookie or session to make the key user-specific
  if (typeof window !== 'undefined') {
    const userId = localStorage.getItem('user_id') || 'anonymous';
    return `${process.env.NEXT_PUBLIC_STORAGE_KEY || DEFAULT_KEY}-${userId}`;
  }
  return DEFAULT_KEY;
}

export interface EncryptedItem {
  id?: number;
  key: string;
  value: string; // Encrypted string
  timestamp: number;
}

export class OfflineStorage extends Dexie {
  items!: Table<EncryptedItem>;

  constructor() {
    super('OfflineEncryptedDB');
    this.version(1).stores({
      items: '++id, key' // Primary key and indexed props
    });
  }

  private encrypt(data: any): string {
    const key = getEncryptionKey();
    return CryptoJS.AES.encrypt(JSON.stringify(data), key).toString();
  }

  private decrypt(ciphertext: string): any {
    const key = getEncryptionKey();
    try {
      const bytes = CryptoJS.AES.decrypt(ciphertext, key);
      return JSON.parse(bytes.toString(CryptoJS.enc.Utf8));
    } catch (e) {
      console.error("Failed to decrypt data", e);
      return null;
    }
  }

  async setItem(key: string, value: any) {
    const encrypted = this.encrypt(value);
    // Check if exists to update
    const existing = await this.items.where('key').equals(key).first();
    if (existing) {
      await this.items.update(existing.id!, {
        value: encrypted,
        timestamp: Date.now()
      });
    } else {
      await this.items.add({
        key,
        value: encrypted,
        timestamp: Date.now()
      });
    }
  }

  async getItem(key: string) {
    const item = await this.items.where('key').equals(key).first();
    if (!item) return null;
    return this.decrypt(item.value);
  }

  async removeItem(key: string) {
    await this.items.where('key').equals(key).delete();
  }
}

export const offlineStorage = new OfflineStorage();
