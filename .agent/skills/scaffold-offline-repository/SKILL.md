---
name: scaffold-offline-repository
description: Genera un repositorio frontend Offline-First seguro (IndexDB Encriptado + Sync).
author: AppNotion Architecture Team
version: 1.0.0
---

# Skill: Scaffold Offline Repository

Esta skill genera la capa de datos del cliente para soportar funcionamiento Offline-First con máxima seguridad.

## Arquitectura

- **Almacenamiento**: Dexie.js (Wrapper de IndexedDB).
- **Seguridad**: Cifrado AES-GCM usando Web Crypto API antes de persistir en disco.
- **Sincronización**: Estrategia "Background Sync" (Cola de mutaciones).

## Prerrequisitos

- [ ] `npm install dexie`
- [ ] `npm install husky` (para hooks, opcional)

## Template de Implementación

### 1. Definir Schema (db.ts)

Crea `src/lib/db/index.ts`:

```typescript
import Dexie, { Table } from "dexie";

export interface EncryptedItem {
  id: string;
  iv: Uint8Array;
  data: ArrayBuffer; // Cifrado
  updated_at: number;
  sync_status: "synced" | "pending" | "conflict";
}

export class AppDatabase extends Dexie {
  diagrams!: Table<EncryptedItem>;

  constructor() {
    super("AppNotionDB");
    this.version(1).stores({
      diagrams: "id, sync_status, updated_at",
    });
  }
}

export const db = new AppDatabase();
```

### 2. Servicio de Encriptación (crypto.ts)

Crea `src/lib/services/crypto-service.ts`:

```typescript
// Implementación básica de AES-GCM
// Nota: La Key debe derivarse del PIN del usuario o JWT, no guardarse en texto plano.
export class CryptoService {
  private key: CryptoKey | null = null;

  async init(secret: string) {
    // Derivar key usando PBKDF2...
  }

  async encrypt(data: any): Promise<{ iv: Uint8Array; content: ArrayBuffer }> {
    // ...
  }

  async decrypt(iv: Uint8Array, content: ArrayBuffer): Promise<any> {
    // ...
  }
}
```

### 3. Hook de Repositorio (useRepository.ts)

Abstrae la lógica:

```typescript
export function useRepository<T>(table: string) {
  const { liveQuery } = useLiveQuery(() => db.table(table).toArray());

  const save = async (item: T) => {
    // 1. Encriptar
    const encrypted = await crypto.encrypt(item);
    // 2. Guardar Local (Optimistic UI)
    await db.table(table).put({
      ...encrypted,
      sync_status: "pending",
    });
    // 3. Intentar Sync
    try {
      await api.post("/sync", item);
      await db.table(table).update(item.id, { sync_status: "synced" });
    } catch {
      // Queda en pending para el Service Worker
    }
  };

  return { items: liveQuery, save };
}
```

## Checklist de Seguridad PWA

- [ ] **Zero Knowledge**: ¿El servidor recibe los datos encriptados O los datos se desencriptan para procesamiento? (Definir modelo).
- [ ] **Key Management**: ¿Dónde vive la llave de encriptación local? (SessionStorage es volátil, IndexDB es inseguro si no está encriptada ella misma).
- [ ] **Performance**: No bloquear el Main Thread al encriptar blobs grandes (usar Web Workers).
