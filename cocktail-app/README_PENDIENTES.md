# Pendientes posteriores al refactor cliente-servidor

Este documento reúne el trabajo necesario para llevar la aplicación desde el
refactor funcional a un nivel seguro, mantenible y desplegable. Las prioridades
se ordenan por riesgo e impacto: `P0` debe resolverse antes de publicar una
versión accesible fuera del equipo de desarrollo.

## P0 — Bloqueantes de seguridad y operación

### Seguridad y gestión de secretos

- [x] Mover `SECRET_KEY`, URL de base de datos, orígenes CORS, credenciales
  iniciales y demás configuración sensible a variables de entorno validadas al
  arrancar la aplicación.
- [x] Añadir un archivo `.env.example` sin valores reales y asegurar que `.env`,
  bases de datos locales, directorios de subida y entornos virtuales estén
  ignorados por Git.
- [x] Eliminar credenciales por defecto, accesos de diagnóstico y cualquier
  secreto embebido en el código.
- [x] Restringir CORS a los orígenes configurados. **Pendiente:** terminar la
  configuración de HTTPS en el entorno de producción.
- [x] Validar y limitar las cargas de archivos: autenticación, tipo MIME,
  extensión, tamaño máximo, nombre generado por el servidor y protección contra
  recorridos de directorio.

**Criterios de finalización verificables**

- La aplicación no inicia si falta una variable crítica y explica cuál falta sin
  revelar secretos.
- Una búsqueda por `SECRET`, `PASSWORD` y claves conocidas no encuentra valores
  sensibles en archivos versionados.
- Un origen no autorizado no recibe cabeceras CORS; uno autorizado sí.
- Las pruebas de carga rechazan archivos ejecutables, extensiones falsas,
  nombres con `../` y archivos que exceden el límite configurado.

### Gestión de usuarios y roles

- [x] Definir roles explícitos (`admin`, `editor` y `customer`) y permisos por
  operación, en vez de depender únicamente de que exista un JWT válido.
- [x] Limitar la creación, desactivación y cambio de rol de usuarios a
  administradores autorizados; establecer un flujo seguro para el primer
  administrador.
- [x] Incluir expiración configurable de sesión y respuestas uniformes ante
  sesiones inválidas. **Pendiente:** implementar revocación/rotación si el
  despliegue lo requiere.
- [x] No registrar contraseñas, tokens ni datos de autenticación en consola o
  logs.

**Criterios de finalización verificables**

- Una petición sin token responde `401`, una con permiso insuficiente `403` y
  un administrador autorizado puede completar el flujo esperado.
- No existe un endpoint público que permita escalar privilegios.
- Las pruebas cubren al menos los casos de token vencido, token inválido,
  usuario desactivado y acceso por rol.

## P1 — Estabilidad, datos y calidad

### Migraciones y preparación para producción

- [ ] Sustituir la creación automática de tablas por migraciones versionadas
  (por ejemplo, Alembic) y documentar el procedimiento de actualización y
  reversión.
- [ ] Mantener SQLite únicamente para desarrollo y configurar PostgreSQL para
  los entornos compartidos o de producción.
- [x] Usar rutas absolutas configurables para la base de datos y el
  almacenamiento de imágenes, para que el directorio de trabajo no cambie el
  comportamiento.
- [ ] Definir copias de seguridad, restauración y una política de retención de
  datos e imágenes.

**Criterios de finalización verificables**

- En una base vacía, el comando de migración crea el esquema completo sin
  ejecutar código de siembra involuntario.
- Una migración de ejemplo se aplica y revierte en una base temporal.
- La aplicación se conecta a PostgreSQL mediante configuración de entorno y
  ejecuta su suite de pruebas de integración.
- Se puede restaurar una copia de seguridad documentada en un entorno aislado.

### Pruebas y CI

- [ ] Añadir pruebas unitarias para servicios, validaciones, autorización y
  adaptación de datos.
- [ ] Añadir pruebas de API para autenticación, CRUD de cócteles, paginación,
  filtros, errores y cargas de imágenes.
- [ ] Añadir pruebas de interfaz para estados de carga, vacío, error, formulario
  de administración y cierre de sesión.
- [ ] Configurar linting, formateo, comprobación de dependencias y ejecución de
  pruebas en integración continua.

**Criterios de finalización verificables**

- Los comandos documentados de pruebas de backend y frontend terminan con
  código `0` en una instalación limpia.
- Cada cambio en una rama ejecuta lint, build y pruebas en CI; un fallo bloquea
  la integración.
- Los flujos críticos cubren respuestas `200`, `201`, `400`, `401`, `403`,
  `404` y validación de errores en pruebas automatizadas.

### Contrato y evolución de la API

- [x] Mantener un contrato único versionado bajo `/api/v1` y eliminar rutas o
  servidores heredados cuando todos los clientes hayan migrado.
- [x] Documentar paginación, filtros, ordenamiento, formatos de error y el DTO
  de cóctel en OpenAPI y en el README.
- [x] Centralizar el cliente HTTP del frontend, incluyendo URL base por entorno,
  encabezado de autorización y manejo consistente de errores `401`.

**Criterios de finalización verificables**

- El catálogo público y el panel administrativo consumen la misma API y no
  realizan llamadas directas a una fuente externa desde componentes.
- La documentación OpenAPI muestra y valida todos los endpoints públicos.
- Un cambio incompatible se publica en una nueva versión de API o cuenta con un
  plan de deprecación documentado.

## P2 — Experiencia, observabilidad y mantenibilidad

### Observabilidad

- [ ] Implementar logs estructurados con nivel, identificador de solicitud,
  usuario anonimizado, ruta, método, estado y duración.
- [x] Exponer endpoints de salud y preparación (`/health` y `/ready`) sin datos
  sensibles.
- [ ] Registrar métricas operativas: latencia, tasa de errores, autenticaciones,
  cargas de imágenes y disponibilidad de base de datos.
- [ ] Configurar alertas para errores sostenidos, fallos de base de datos y uso
  anómalo de almacenamiento.

**Criterios de finalización verificables**

- Cada respuesta de la API puede correlacionarse con un identificador de
  solicitud en los logs.
- Los endpoints de salud diferencian entre proceso vivo y dependencia lista.
- Se puede consultar un panel o salida agregada con errores 5xx y latencia por
  endpoint durante una prueba controlada.

### Gestión de imágenes

- [ ] Separar el almacenamiento de medios de los archivos estáticos de la
  aplicación; usar volumen persistente en desarrollo y almacenamiento de
  objetos/CDN en producción cuando corresponda.
- [ ] Generar nombres únicos, miniaturas y variantes optimizadas; conservar
  `alt` descriptivo como parte de los datos del cóctel.
- [ ] Eliminar de forma controlada las imágenes huérfanas y definir qué ocurre
  al reemplazar o borrar un cóctel.

**Criterios de finalización verificables**

- Dos cargas con el mismo nombre no sobrescriben contenido existente.
- Las tarjetas cargan una variante optimizada y el detalle puede acceder a la
  imagen adecuada.
- Una eliminación de cóctel no deja medios sin referencia, según una tarea de
  limpieza comprobable.

### Accesibilidad y experiencia de usuario

- [ ] Usar elementos semánticos, etiquetas asociadas a controles, foco visible,
  navegación completa por teclado y contraste suficiente.
- [ ] Gestionar el foco y el cierre con `Escape` en modales; anunciar errores y
  estados de carga mediante regiones accesibles.
- [ ] Proporcionar textos alternativos útiles, estados vacíos y mensajes de
  error recuperables en catálogo, autenticación y administración.
- [ ] Verificar diseño adaptable en móvil, tableta y escritorio.

**Criterios de finalización verificables**

- Se completa la búsqueda, inicio de sesión y CRUD básico usando solo teclado.
- Un análisis automatizado de accesibilidad no informa errores críticos ni de
  contraste en las rutas principales.
- Las pruebas manuales en anchos de 320 px, 768 px y 1280 px no producen
  desbordamiento horizontal ni controles inaccesibles.

## P3 — Entrega y despliegue

### Despliegue reproducible

- [ ] Crear imágenes de contenedor para frontend y backend, con dependencias
  bloqueadas y un `docker-compose` para desarrollo integrado.
- [ ] Definir variables de entorno por ambiente, un proxy inverso/TLS y una
  configuración separada para desarrollo, pruebas y producción.
- [ ] Automatizar el despliegue únicamente después de aprobar build, pruebas,
  migraciones y comprobaciones de salud.
- [ ] Documentar configuración, arranque local, despliegue, reversión y
  respuesta ante incidentes.

**Criterios de finalización verificables**

- Una persona nueva puede levantar el sistema completo con el procedimiento
  documentado y acceder al frontend, API, documentación y persistencia.
- Una publicación en entorno de prueba ejecuta migraciones, pasa health checks
  y permite volver a la versión anterior sin pérdida de datos.
- Las imágenes de contenedor no se ejecutan como `root`, no incluyen secretos y
  superan el análisis de vulnerabilidades acordado por el equipo.

## Estado tras las correcciones de octubre de 2026

La API versionada, roles, sesión por cookie HTTP-only, registro de clientes,
catálogo, cálculo de costos, carga validada de imágenes, servicios, pedidos y
flujo de pago Wompi con verificación de eventos están implementados en el
código. **No se han ejecutado pruebas automatizadas en esta entrega.** Los pagos
requieren credenciales Wompi y una URL HTTPS pública; el catálogo del negocio y
los datos de contacto deben completarse con precios e información reales. La
migración SQLite es aditiva, pero todavía no sustituye a Alembic.

## Revisión de cierre

Antes de declarar el proyecto listo, comprobar que todos los puntos `P0` y
`P1` estén completados, que no queden secretos ni archivos generados en el
control de versiones y que la demostración cubra catálogo público,
autenticación, autorización, CRUD, imagen, prueba automatizada y despliegue
desde una instalación limpia.
