---
name: scaffold-offline-repository
description: Genera un repositorio frontend Offline-First seguro (IndexedDB Encriptado + Sync).
author: AppNotion Architecture Team
version: 2.0.0
---

# Skill: Scaffold Offline Repository

Esta skill genera la capa de datos del cliente para soportar funcionamiento Offline-First con máxima seguridad, siguiendo el patrón Repository con encriptación AES-GCM.

## Arquitectura

```
frontend/src/lib/
├── db/
│   ├── index.ts              # Dexie database schema
│   └── migrations.ts         # Versiones del schema
├── services/
│   ├── crypto-service.ts     # Encriptación AES-GCM
│   └── sync-service.ts       # Sincronización con backend
├── repositories/
│   └── diagram-repository.ts # Repository pattern
└── hooks/
    └── use-repository.ts     # React hook abstraction
```

## Prerrequisitos

- [ ] Instalar dependencias:
  ```bash
  npm install dexie dexie-react-hooks
  ```
- [ ] Tener API backend con endpoint de sync.

## Cuándo Usar

- Al implementar funcionalidad offline (PWA).
- Para datos sensibles que requieren encriptación local.
- Cuando se necesita sincronización optimista (Optimistic UI).

---

## Templates de Implementación

### 1. Database Schema (db/index.ts)

**Archivo:** `frontend/src/lib/db/index.ts`

```typescript
import Dexie, { Table } from "dexie";

/**
 * Encrypted item stored in IndexedDB.
 * Raw data is never stored - only encrypted blobs.
 */
export interface EncryptedItem {
    id: string;
    iv: string; // Base64 encoded initialization vector
    data: string; // Base64 encoded encrypted data
    updated_at: number;
    sync_status: "synced" | "pending" | "conflict";
    version: number; // For conflict resolution
}

/**
 * Pending mutation for background sync.
 */
export interface PendingMutation {
    id: string;
    type: "create" | "update" | "delete";
    entity_type: string;
    entity_id: string;
    payload: string; // Encrypted payload
    created_at: number;
    retry_count: number;
}

/**
 * AppNotion local database.
 * Uses Dexie.js as IndexedDB wrapper.
 */
export class AppDatabase extends Dexie {
    diagrams!: Table<EncryptedItem>;
    settings!: Table<EncryptedItem>;
    pendingMutations!: Table<PendingMutation>;

    constructor() {
        super("AppNotionDB");

        // Schema versioning
        this.version(1).stores({
            diagrams: "id, sync_status, updated_at",
            settings: "id",
            pendingMutations: "id, entity_type, created_at",
        });

        // Future migrations
        this.version(2).stores({
            // Add new tables or indexes here
        });
    }
}

export const db = new AppDatabase();

// Export singleton for use across app
export default db;
```

### 2. Crypto Service (services/crypto-service.ts)

**Archivo:** `frontend/src/lib/services/crypto-service.ts`

```typescript
/**
 * CryptoService
 * Handles AES-GCM encryption/decryption using Web Crypto API.
 *
 * Security notes:
 * - Key is derived from user secret (JWT token or PIN)
 * - IV is unique per encryption operation
 * - Never store the key in IndexedDB or localStorage
 */

const ALGORITHM = "AES-GCM";
const KEY_LENGTH = 256;
const IV_LENGTH = 12; // 96 bits recommended for GCM

export class CryptoService {
    private key: CryptoKey | null = null;
    private initialized = false;

    /**
     * Initialize the crypto service with a user secret.
     * Call this after user authentication.
     *
     * @param secret - User's JWT token or derived secret
     */
    async init(secret: string): Promise<void> {
        if (this.initialized) return;

        // Derive a key from the secret using PBKDF2
        const encoder = new TextEncoder();
        const keyMaterial = await crypto.subtle.importKey(
            "raw",
            encoder.encode(secret),
            "PBKDF2",
            false,
            ["deriveBits", "deriveKey"]
        );

        // Use a fixed salt (could be user ID for per-user keys)
        const salt = encoder.encode("AppNotion-v1-salt");

        this.key = await crypto.subtle.deriveKey(
            {
                name: "PBKDF2",
                salt,
                iterations: 100000,
                hash: "SHA-256",
            },
            keyMaterial,
            { name: ALGORITHM, length: KEY_LENGTH },
            false, // Not extractable
            ["encrypt", "decrypt"]
        );

        this.initialized = true;
    }

    /**
     * Encrypt data using AES-GCM.
     *
     * @param data - Plain object to encrypt
     * @returns Encrypted data with IV
     */
    async encrypt<T>(data: T): Promise<{ iv: string; content: string }> {
        if (!this.key) {
            throw new Error("CryptoService not initialized. Call init() first.");
        }

        // Generate random IV for each encryption
        const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH));

        // Serialize and encode data
        const encoder = new TextEncoder();
        const encoded = encoder.encode(JSON.stringify(data));

        // Encrypt
        const encrypted = await crypto.subtle.encrypt(
            { name: ALGORITHM, iv },
            this.key,
            encoded
        );

        // Convert to Base64 for storage
        return {
            iv: this.arrayBufferToBase64(iv),
            content: this.arrayBufferToBase64(encrypted),
        };
    }

    /**
     * Decrypt data using AES-GCM.
     *
     * @param iv - Base64 encoded initialization vector
     * @param content - Base64 encoded encrypted data
     * @returns Decrypted object
     */
    async decrypt<T>(iv: string, content: string): Promise<T> {
        if (!this.key) {
            throw new Error("CryptoService not initialized. Call init() first.");
        }

        // Decode from Base64
        const ivBuffer = this.base64ToArrayBuffer(iv);
        const contentBuffer = this.base64ToArrayBuffer(content);

        // Decrypt
        const decrypted = await crypto.subtle.decrypt(
            { name: ALGORITHM, iv: ivBuffer },
            this.key,
            contentBuffer
        );

        // Decode and parse
        const decoder = new TextDecoder();
        return JSON.parse(decoder.decode(decrypted));
    }

    /**
     * Clear the key from memory.
     * Call this on logout.
     */
    destroy(): void {
        this.key = null;
        this.initialized = false;
    }

    // Utility: ArrayBuffer to Base64
    private arrayBufferToBase64(buffer: ArrayBuffer | Uint8Array): string {
        const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
        let binary = "";
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }

    // Utility: Base64 to ArrayBuffer
    private base64ToArrayBuffer(base64: string): ArrayBuffer {
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes.buffer;
    }
}

// Export singleton
export const cryptoService = new CryptoService();
```

### 3. Sync Service (services/sync-service.ts)

**Archivo:** `frontend/src/lib/services/sync-service.ts`

```typescript
import { db, PendingMutation } from "@/lib/db";

/**
 * SyncService
 * Handles background synchronization with the backend.
 * Uses a queue-based approach for reliability.
 */

export interface SyncResult {
    success: boolean;
    synced: number;
    failed: number;
    conflicts: string[];
}

export class SyncService {
    private apiUrl: string;
    private isOnline: boolean = navigator.onLine;
    private syncInProgress: boolean = false;

    constructor(apiUrl: string) {
        this.apiUrl = apiUrl;
        this.setupListeners();
    }

    /**
     * Setup online/offline event listeners.
     */
    private setupListeners(): void {
        window.addEventListener("online", () => {
            this.isOnline = true;
            this.processPendingMutations();
        });

        window.addEventListener("offline", () => {
            this.isOnline = false;
        });
    }

    /**
     * Queue a mutation for sync.
     * Called when user performs an action offline.
     */
    async queueMutation(
        type: "create" | "update" | "delete",
        entityType: string,
        entityId: string,
        payload: string
    ): Promise<void> {
        const mutation: PendingMutation = {
            id: crypto.randomUUID(),
            type,
            entity_type: entityType,
            entity_id: entityId,
            payload,
            created_at: Date.now(),
            retry_count: 0,
        };

        await db.pendingMutations.add(mutation);

        // Try to sync immediately if online
        if (this.isOnline) {
            this.processPendingMutations();
        }
    }

    /**
     * Process all pending mutations.
     * Called on app start and when coming back online.
     */
    async processPendingMutations(): Promise<SyncResult> {
        if (this.syncInProgress || !this.isOnline) {
            return { success: false, synced: 0, failed: 0, conflicts: [] };
        }

        this.syncInProgress = true;
        const result: SyncResult = {
            success: true,
            synced: 0,
            failed: 0,
            conflicts: [],
        };

        try {
            const mutations = await db.pendingMutations
                .orderBy("created_at")
                .toArray();

            for (const mutation of mutations) {
                try {
                    await this.syncMutation(mutation);
                    await db.pendingMutations.delete(mutation.id);
                    result.synced++;
                } catch (error: any) {
                    if (error.status === 409) {
                        // Conflict - needs manual resolution
                        result.conflicts.push(mutation.entity_id);
                        await this.markAsConflict(mutation.entity_id);
                    } else {
                        // Retry later
                        await this.incrementRetryCount(mutation.id);
                        result.failed++;
                    }
                }
            }
        } finally {
            this.syncInProgress = false;
        }

        return result;
    }

    /**
     * Sync a single mutation to the backend.
     */
    private async syncMutation(mutation: PendingMutation): Promise<void> {
        const endpoint = `${this.apiUrl}/${mutation.entity_type}`;

        let url = endpoint;
        let method = "POST";

        switch (mutation.type) {
            case "create":
                method = "POST";
                break;
            case "update":
                method = "PUT";
                url = `${endpoint}/${mutation.entity_id}`;
                break;
            case "delete":
                method = "DELETE";
                url = `${endpoint}/${mutation.entity_id}`;
                break;
        }

        const response = await fetch(url, {
            method,
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${this.getAuthToken()}`,
            },
            body: mutation.type !== "delete" ? mutation.payload : undefined,
        });

        if (!response.ok) {
            const error = new Error("Sync failed");
            (error as any).status = response.status;
            throw error;
        }
    }

    private async markAsConflict(entityId: string): Promise<void> {
        await db.diagrams.update(entityId, { sync_status: "conflict" });
    }

    private async incrementRetryCount(mutationId: string): Promise<void> {
        const mutation = await db.pendingMutations.get(mutationId);
        if (mutation && mutation.retry_count < 5) {
            await db.pendingMutations.update(mutationId, {
                retry_count: mutation.retry_count + 1,
            });
        } else if (mutation) {
            // Max retries exceeded - remove from queue
            await db.pendingMutations.delete(mutationId);
        }
    }

    private getAuthToken(): string {
        // Get from your auth store
        return localStorage.getItem("access_token") || "";
    }
}

// Export singleton
export const syncService = new SyncService(
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010/api/v1"
);
```

### 4. Repository Hook (hooks/use-repository.ts)

**Archivo:** `frontend/src/lib/hooks/use-repository.ts`

```typescript
"use client";

import { useState, useEffect, useCallback } from "react";
import { useLiveQuery } from "dexie-react-hooks";
import { db, EncryptedItem } from "@/lib/db";
import { cryptoService } from "@/lib/services/crypto-service";
import { syncService } from "@/lib/services/sync-service";

interface UseRepositoryOptions<T> {
    tableName: "diagrams" | "settings";
    entityType: string;
}

interface RepositoryState<T> {
    items: T[];
    loading: boolean;
    error: Error | null;
}

interface RepositoryActions<T> {
    save: (item: T & { id: string }) => Promise<void>;
    remove: (id: string) => Promise<void>;
    refresh: () => Promise<void>;
}

/**
 * useRepository
 * React hook for offline-first data access with encryption.
 *
 * @example
 * const { items, loading, save, remove } = useRepository<Diagram>({
 *   tableName: "diagrams",
 *   entityType: "diagrams"
 * });
 */
export function useRepository<T extends object>(
    options: UseRepositoryOptions<T>
): RepositoryState<T> & RepositoryActions<T> {
    const { tableName, entityType } = options;
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);
    const [decryptedItems, setDecryptedItems] = useState<T[]>([]);

    // Live query for encrypted items
    const encryptedItems = useLiveQuery(
        () => db[tableName].toArray(),
        [tableName]
    );

    // Decrypt items when they change
    useEffect(() => {
        async function decryptAll() {
            if (!encryptedItems) return;

            setLoading(true);
            try {
                const decrypted = await Promise.all(
                    encryptedItems.map(async (item) => {
                        try {
                            return await cryptoService.decrypt<T>(item.iv, item.data);
                        } catch (e) {
                            console.error(`Failed to decrypt item ${item.id}`, e);
                            return null;
                        }
                    })
                );
                setDecryptedItems(decrypted.filter((item): item is T => item !== null));
            } catch (e) {
                setError(e as Error);
            } finally {
                setLoading(false);
            }
        }

        decryptAll();
    }, [encryptedItems]);

    /**
     * Save an item (create or update).
     * Uses optimistic UI - updates local first, then syncs.
     */
    const save = useCallback(
        async (item: T & { id: string }) => {
            try {
                // 1. Encrypt
                const encrypted = await cryptoService.encrypt(item);

                // 2. Save locally (optimistic)
                const encryptedItem: EncryptedItem = {
                    id: item.id,
                    iv: encrypted.iv,
                    data: encrypted.content,
                    updated_at: Date.now(),
                    sync_status: "pending",
                    version: 1,
                };

                const existing = await db[tableName].get(item.id);
                if (existing) {
                    encryptedItem.version = existing.version + 1;
                    await db[tableName].update(item.id, encryptedItem);
                } else {
                    await db[tableName].add(encryptedItem);
                }

                // 3. Queue for sync
                await syncService.queueMutation(
                    existing ? "update" : "create",
                    entityType,
                    item.id,
                    JSON.stringify(item)
                );
            } catch (e) {
                setError(e as Error);
                throw e;
            }
        },
        [tableName, entityType]
    );

    /**
     * Remove an item.
     */
    const remove = useCallback(
        async (id: string) => {
            try {
                // 1. Delete locally
                await db[tableName].delete(id);

                // 2. Queue for sync
                await syncService.queueMutation("delete", entityType, id, "");
            } catch (e) {
                setError(e as Error);
                throw e;
            }
        },
        [tableName, entityType]
    );

    /**
     * Force refresh from backend.
     */
    const refresh = useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/${entityType}`,
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
                    },
                }
            );

            if (!response.ok) throw new Error("Failed to fetch");

            const items: T[] = await response.json();

            // Encrypt and store each item
            for (const item of items as (T & { id: string })[]) {
                const encrypted = await cryptoService.encrypt(item);
                await db[tableName].put({
                    id: item.id,
                    iv: encrypted.iv,
                    data: encrypted.content,
                    updated_at: Date.now(),
                    sync_status: "synced",
                    version: 1,
                });
            }
        } catch (e) {
            setError(e as Error);
        } finally {
            setLoading(false);
        }
    }, [tableName, entityType]);

    return {
        items: decryptedItems,
        loading,
        error,
        save,
        remove,
        refresh,
    };
}
```

### 5. Ejemplo de Uso

```tsx
"use client";

import { useRepository } from "@/lib/hooks/use-repository";
import { useEffect } from "react";
import { cryptoService } from "@/lib/services/crypto-service";
import { useAuth } from "@/hooks/use-auth";

interface Diagram {
    id: string;
    name: string;
    nodes: any[];
    edges: any[];
}

export function DiagramList() {
    const { token } = useAuth();
    const { items, loading, save, remove } = useRepository<Diagram>({
        tableName: "diagrams",
        entityType: "diagrams",
    });

    // Initialize crypto with user token
    useEffect(() => {
        if (token) {
            cryptoService.init(token);
        }
    }, [token]);

    const handleCreate = async () => {
        const newDiagram: Diagram = {
            id: crypto.randomUUID(),
            name: "New Diagram",
            nodes: [],
            edges: [],
        };
        await save(newDiagram);
    };

    if (loading) return <div>Loading...</div>;

    return (
        <div>
            <button onClick={handleCreate}>Create Diagram</button>
            {items.map((diagram) => (
                <div key={diagram.id}>
                    <span>{diagram.name}</span>
                    <button onClick={() => remove(diagram.id)}>Delete</button>
                </div>
            ))}
        </div>
    );
}
```

---

## Checklist de Seguridad PWA

### Encriptación
- [ ] Key derivada de secreto del usuario (no hardcodeada)
- [ ] IV único por operación de encriptación
- [ ] Key no exportable (`extractable: false`)
- [ ] Key limpiada en logout (`cryptoService.destroy()`)

### Almacenamiento
- [ ] Solo datos encriptados en IndexedDB
- [ ] No almacenar tokens en IndexedDB
- [ ] Usar `sessionStorage` para datos de sesión

### Sincronización
- [ ] Queue de mutaciones persistente
- [ ] Retry con exponential backoff
- [ ] Manejo de conflictos
- [ ] Limpieza de datos expirados

### Performance
- [ ] Encriptación en Web Worker para datos grandes
- [ ] Paginación de queries a IndexedDB
- [ ] Lazy loading de datos

---

## Errores Comunes

### Error: "CryptoService not initialized"

**Causa:** Intentar encriptar/desencriptar sin llamar `init()`.

**Solución:** Inicializar después de autenticación:
```tsx
useEffect(() => {
    if (token) cryptoService.init(token);
}, [token]);
```

### Error: Datos corruptos después de actualización

**Causa:** Cambio de schema sin migración.

**Solución:** Usar versionado de Dexie correctamente:
```typescript
this.version(2).stores({...}).upgrade(tx => {
    // Migration logic
});
```

### Error: Sync loop infinito

**Causa:** No marcar items como "synced" después de sync exitoso.

**Solución:** Actualizar `sync_status` a "synced" en el callback de éxito.

---

## Referencias

- [Dexie.js Documentation](https://dexie.org/)
- [Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API)
- [Background Sync API](https://developer.mozilla.org/en-US/docs/Web/API/Background_Synchronization_API)

---

*Última actualización: 2025-02-04*
