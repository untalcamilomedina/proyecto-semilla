# Especificación de la API de Administración de Usuarios

Este documento detalla la API RESTful para la gestión de usuarios en el panel de administración.

## Modelo de Datos

### User

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `id` | UUID | Identificador único del usuario. |
| `email` | String | Dirección de correo electrónico (única). |
| `first_name` | String | Nombre del usuario. |
| `last_name` | String | Apellido del usuario. |
| `full_name` | String | Nombre completo (campo calculado). |
| `is_active` | Boolean | Indica si la cuenta del usuario está activa. |
| `is_verified` | Boolean | Indica si el correo ha sido verificado. |
| `tenant_id` | UUID | ID del tenant al que pertenece el usuario. |
| `role_ids` | Array[UUID] | Lista de IDs de los roles asignados. |
| `created_at` | DateTime | Fecha de creación. |
| `updated_at` | DateTime | Fecha de última actualización. |

---

## Endpoints de la API

La URL base para estos endpoints es `/api/v1`.

### Endpoints de Autenticación

#### 1. Iniciar Sesión

- **Endpoint:** `POST /auth/login`
- **Descripción:** Autentica a un usuario y, si tiene éxito, establece una cookie de sesión `HttpOnly` segura.
- **Cuerpo de la Solicitud (`application/x-www-form-urlencoded`):**
  - `username`: El correo electrónico del usuario.
  - `password`: La contraseña del usuario.
- **Respuestas:**
  - `200 OK`: Autenticación exitosa. Devuelve un objeto con el `access_token` y los datos del usuario. La cookie de sesión se establece automáticamente en la respuesta.
  - `400 Bad Request`: Credenciales inválidas o mal formateadas.

#### 2. Registrar un Nuevo Usuario

- **Endpoint:** `POST /auth/register`
- **Descripción:** Crea una nueva cuenta de usuario.
- **Cuerpo de la Solicitud (`application/json`):**
  ```json
  {
    "email": "newuser@example.com",
    "password": "a-strong-password",
    "first_name": "New",
    "last_name": "User"
  }
  ```
- **Respuestas:**
  - `201 Created`: Usuario registrado exitosamente.
  - `400 Bad Request`: Datos de entrada inválidos.
  - `409 Conflict`: El correo electrónico ya está en uso.

#### 3. Obtener el Usuario Actual

- **Endpoint:** `GET /auth/me`
- **Descripción:** Devuelve los detalles del usuario autenticado actualmente, validando la sesión a través de la cookie `HttpOnly`.
- **Respuestas:**
  - `200 OK`: Detalles del usuario.
  - `401 Unauthorized`: Sesión no válida o expirada.

#### 4. Cerrar Sesión

- **Endpoint:** `POST /auth/logout`
- **Descripción:** Invalida la sesión del usuario actual eliminando la cookie de sesión del navegador.
- **Respuestas:**
  - `200 OK`: Sesión cerrada exitosamente.

---

### Endpoints de Gestión de Usuarios

### 1. Crear un Nuevo Usuario

- **Endpoint:** `POST /users/`
- **Descripción:** Crea un nuevo usuario en el sistema. Requiere permisos de administrador.
- **Cuerpo de la Solicitud (`application/json`):**
  ```json
  {
    "email": "user@example.com",
    "password": "a-strong-password",
    "first_name": "John",
    "last_name": "Doe",
    "tenant_id": "uuid-of-the-tenant",
    "role_ids": ["uuid-of-a-role"]
  }
  ```
- **Respuestas:**
  - `201 Created`: Usuario creado exitosamente. Devuelve el objeto del usuario creado.
  - `400 Bad Request`: Datos de entrada inválidos.
  - `409 Conflict`: El correo electrónico ya existe.
  - `403 Forbidden`: Sin permisos suficientes.

### 2. Obtener una Lista de Usuarios

- **Endpoint:** `GET /users/`
- **Descripción:** Devuelve una lista paginada de usuarios.
- **Parámetros de Consulta:**
  - `skip` (opcional, `int`, default: 0): Número de registros a omitir.
  - `limit` (opcional, `int`, default: 100): Número máximo de registros a devolver.
- **Respuestas:**
  - `200 OK`: Lista de usuarios.
    ```json
    [
      {
        "id": "user-uuid-1",
        "email": "user1@example.com",
        ...
      },
      {
        "id": "user-uuid-2",
        "email": "user2@example.com",
        ...
      }
    ]
    ```

### 3. Obtener un Usuario Específico

- **Endpoint:** `GET /users/{user_id}`
- **Descripción:** Devuelve los detalles de un usuario por su ID.
- **Parámetros de Ruta:**
  - `user_id` (requerido, `UUID`): El ID del usuario a obtener.
- **Respuestas:**
  - `200 OK`: Detalles del usuario.
  - `404 Not Found`: Usuario no encontrado.

### 4. Actualizar un Usuario

- **Endpoint:** `PUT /users/{user_id}`
- **Descripción:** Actualiza la información de un usuario existente.
- **Parámetros de Ruta:**
  - `user_id` (requerido, `UUID`): El ID del usuario a actualizar.
- **Cuerpo de la Solicitud (`application/json`):**
  ```json
  {
    "email": "new.email@example.com",
    "first_name": "Jane",
    "is_active": false,
    "role_ids": ["new-role-uuid"]
  }
  ```
- **Respuestas:**
  - `200 OK`: Usuario actualizado exitosamente. Devuelve el objeto del usuario actualizado.
  - `400 Bad Request`: Datos de entrada inválidos.
  - `404 Not Found`: Usuario no encontrado.
  - `403 Forbidden`: Sin permisos suficientes.

### 5. Eliminar un Usuario

- **Endpoint:** `DELETE /users/{user_id}`
- **Descripción:** Elimina un usuario del sistema.
- **Parámetros de Ruta:**
  - `user_id` (requerido, `UUID`): El ID del usuario a eliminar.
- **Respuestas:**
  - `204 No Content`: Usuario eliminado exitosamente.
  - `404 Not Found`: Usuario no encontrado.
  - `403 Forbidden`: Sin permisos suficientes.