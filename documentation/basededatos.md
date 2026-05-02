# Documentación de la Base de Datos

## Visión General

Este sistema representa una aplicación de **ecommerce** con un módulo interno de **backoffice**, **inventario**,**auth**, **employee**, **customer**,**api**,**store**,**product**.

La aplicación está dividida en tres grandes áreas:

* **Frontend (clientes):** donde los usuarios compran productos
* **Backoffice (empleados):** donde se gestionan productos, inventario y operaciones
* **Api**: donde aplicaciones externas interactuan con los datos de la aplicacion

El inventario es solo una parte del sistema, no el objetivo principal.

---

## tabla: User (Personalizado)

### Descripción

tabla central de autenticación que maneja tanto clientes como empleados.

### Campos importantes

* email: identificador del usuario
* role: define si es `customer` o `employee`
* status: estado del usuario
* is_active: indica si el usuario está activo
* is_staff: acceso al backoffice
* is_superuser: control total del sistema

### Propósito

Unificar todos los tipos de usuarios en un solo tabla, diferenciando su comportamiento mediante roles.

Permite:

* Clientes accediendo al ecommerce
* Empleados accediendo al backoffice

---

## tabla: customer_model

### Descripción

Extiende la información de los usuarios con rol de cliente.

### Campos

* user: relación con User
* phone: teléfono
* address: dirección
* created_at: fecha de registro

### Propósito

Gestionar información adicional necesaria para el proceso de compra.

Ejemplos:

* Datos de contacto
* Dirección para envíos

---

## tabla: employee_model

### Descripción

Extiende la información de los usuarios que trabajan en el sistema.

### Campos

* user: relación con User
* position: cargo dentro de la empresa
* hired_at: fecha de contratación
* is_active: estado laboral

### Propósito

Controlar el acceso al backoffice y la gestión interna.

Permite:

* Definir quién puede administrar el sistema
* Organizar roles internos
* Mantener información del personal

---

## tabla: product

### Descripción

Representa los productos disponibles en la tienda.

### Campos

* name: nombre del producto
* description: descripción
* category: categoría
* status: estado (ej: ACTIVE)
* brand: marca
* image: imagen del producto
* metric_unit: unidad de medida

### Propósito

Es el núcleo del ecommerce.

Se utiliza para:

* Mostrar productos en el frontend
* Gestionar catálogo desde el backoffice

---

## tabla: price

### Descripción

Define el precio de un producto en un momento específico.

### Campos

* product: relación con product
* value: precio
* created_at: fecha de creación

### Propósito

Permitir cambios de precio sin perder historial.

Esto es útil para:

* Ofertas
* Cambios de mercado
* Análisis de precios

---

## tabla: provider

### Descripción

Representa proveedores de productos.

### Campos

* name: nombre
* phone_number: teléfono
* address: dirección
* email: correo
* description: descripción

### Propósito

Gestionar el origen de los productos dentro del backoffice.

Permite:

* Control de abastecimiento
* Registro de relaciones comerciales

---

## tabla: stockentry

### Descripción

Registra entradas de productos al inventario.

### Campos

* product: producto
* provider: proveedor (opcional)
* quantity: cantidad
* cost_per_unit: costo por unidad
* received_at: fecha
* added_by: empleado que registra
* note: nota

### Propósito

Controlar cómo se abastece el inventario.

Se usa en el backoffice para:

* Registrar compras a proveedores
* Inicializar stock
* Ajustes manuales

---

## tabla: stockmovement_model

### Descripción

Registra todos los movimientos de inventario.

### Campos

* date_time: fecha y hora
* product: producto
* movement_type: tipo de movimiento
* document_reference: referencia
* quantity: cantidad
* balance: balance final

### Propósito

Mantener trazabilidad completa del stock.

Se utiliza para:

* Registrar ventas (salidas de inventario)
* Registrar entradas
* Auditar cambios

---

## Relaciones entre tablas

User
├── customer_model
└── employee_model

product
├── price
├── stockentry
└── stockmovement_model

provider
└── stockentry

---

## Flujo del Sistema

### Flujo de Cliente (Frontend)

1. El cliente se registra como User con rol `customer`
2. Consulta productos desde product
3. Visualiza precios desde price
4. Realiza compras (reflejadas como movimientos de inventario)

---

### Flujo de Empleado (Backoffice)

1. El empleado accede al sistema (`is_staff = true`)
2. Gestiona productos en product
3. Define precios en price
4. Registra entradas en stockentry
5. Supervisa movimientos en stockmovement_model

---

## Notas Importantes

* El ecommerce es la capa principal del sistema
* El inventario es un módulo interno de soporte
* El backoffice está restringido a empleados

Diferencias clave:

* stockentry: registra entradas físicas
* stockmovement_model: registra todos los cambios (entradas y salidas)

---

## Conclusión

El sistema está diseñado para separar claramente:

* Experiencia de cliente (ecommerce)
* Operación interna (backoffice)

Esto permite:

* Escalabilidad
* Mejor control de permisos
* Mantenimiento más sencillo
