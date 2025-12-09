# Instrucciones para Completar Actualización Instantánea del Badge

## Lo que ya está hecho:

✅ Creado `NotificationContext.jsx` para comunicación entre componentes
✅ Agregado `NotificationProvider` en `App.js`
✅ Integrado `useNotifications` en `Sidebar.jsx` con `refreshTrigger` dependency

## Lo que falta hacer manualmente:

### En `QuotationForm.jsx`:

#### 1. Agregar import (línea ~8, después de otros imports):
```javascript
import { useNotifications } from '../../context/NotificationContext';
```

#### 2. Agregar hook dentro del componente (línea ~12, después de `const navigate = useNavigate();`):
```javascript
const { triggerRefresh } = useNotifications();
```

#### 3. En la función `handleApprove` (línea ~243, DESPUÉS de `navigate('/cotizaciones');`):
```javascript
navigate('/cotizaciones');
triggerRefresh(); // Actualizar badge inmediatamente
```

#### 4. En la función `handleReject` (busca la función similar a handleApprove, DESPUÉS del navigate):
```javascript
navigate('/cotizaciones');
triggerRefresh(); // Actualizar badge inmediatamente
```

## Cómo funciona:

1. Usuario aprueba/rechaza una cotización
2. Se llama `triggerRefresh()` que incrementa el contador en el Context
3. El `Sidebar` detecta el cambio en `refreshTrigger` (dependency en useEffect)
4. Se ejecuta inmediatamente `fetchPendingStats()` sin esperar 30 segundos
5. El badge se actualiza al instante

## Resultado esperado:

- Badge muestra "2" cotizaciones pendientes
- Usuario aprueba 1 → Badge cambia a "1" INMEDIATAMENTE
- Después de 30s desde la última actualización automática, se vuelve a actualizar
- Si llega una nueva cotización, el badge se actualiza en el próximo ciclo de 30s

## Verificación:

1. Crea 2 cotizaciones públicas
2. Ve al dashboard → Badge muestra "2"
3. Aprueba 1 cotización
4. Badge debe cambiar a "1" sin recargar ni esperar
