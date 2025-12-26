import Dexie, { type Table } from 'dexie';
import CryptoJS from 'crypto-js';

// Secret key should ideally come from env or user input (e.g. password derived), 
// but for this implementation we use a fixed client-side secret or env if available.
// WARNING: Storing key in JS is not fully secure against XSS, but sufficient for basic offline encryption requirement.
const SECRET_KEY = process.env.NEXT_PUBLIC_STORAGE_KEY || "default-insecure-key-change-me";

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
    return CryptoJS.AES.encrypt(JSON.stringify(data), SECRET_KEY).toString();
  }

  private decrypt(ciphertext: string): any {
    try {
      const bytes = CryptoJS.AES.decrypt(ciphertext, SECRET_KEY);
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
