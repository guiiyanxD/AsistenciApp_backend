# Patrón de Diseño: Estrategia (Strategy)

## 1. Teoría del patrón

### Definición

El patrón **Estrategia** es un patrón de comportamiento que permite definir una familia de algoritmos,
encapsular cada uno en una clase separada y hacer que sus objetos sean intercambiables en tiempo de
ejecución, sin que el código que los usa necesite conocer cuál está activo.

> "Define una familia de algoritmos, encapsula cada uno y los hace intercambiables.
> Strategy permite que el algoritmo varíe independientemente de los clientes que lo usan."
> — Gang of Four (GoF)

---

### El problema que resuelve

Sin el patrón, cuando un comportamiento varía según un tipo o condición, el código crece mediante
bloques `if/elif` que se repiten en múltiples lugares. Cada vez que se agrega una variante nueva,
hay que encontrar y modificar todos esos bloques, violando el principio **Open/Closed**
(abierto para extensión, cerrado para modificación).

```python
# Sin Strategy — el problema
def procesar(tipo):
    if tipo == "A":
        # algoritmo A
    elif tipo == "B":
        # algoritmo B
    elif tipo == "C":   # cada nueva variante obliga a modificar este bloque
        # algoritmo C
```

---

### Componentes

| Componente | Rol |
|---|---|
| **Strategy** | Interfaz o clase base que declara el método común a todos los algoritmos |
| **ConcreteStrategy** | Implementación concreta de una variante del algoritmo |
| **Context** | Objeto que usa una Strategy. Delega el trabajo sin conocer la implementación |

---

### Diagrama de clases general

```mermaid
classDiagram
    class Context {
        -strategy : Strategy
        +set_strategy(strategy: Strategy)
        +ejecutar_operacion()
    }

    class Strategy {
        <<interface>>
        +ejecutar(datos)*
    }

    class ConcreteStrategyA {
        +ejecutar(datos)
    }

    class ConcreteStrategyB {
        +ejecutar(datos)
    }

    class ConcreteStrategyC {
        +ejecutar(datos)
    }

    Context o--> Strategy : delega en
    ConcreteStrategyA ..|> Strategy : implementa
    ConcreteStrategyB ..|> Strategy : implementa
    ConcreteStrategyC ..|> Strategy : implementa
```

---

### Diagrama de secuencia general

```mermaid
sequenceDiagram
    actor Cliente
    participant Context
    participant Strategy

    Cliente->>Context: set_strategy(ConcreteStrategyA)
    Cliente->>Context: ejecutar_operacion()
    Context->>Strategy: ejecutar(datos)
    Strategy-->>Context: resultado
    Context-->>Cliente: resultado

    Note over Cliente,Strategy: El Context no cambia.<br/>Solo cambia la Strategy inyectada.
```

---

### Cuándo aplicarlo

- Cuando existen múltiples variantes de un mismo comportamiento que comparten la misma firma.
- Cuando una clase tiene un bloque `if/elif` que crece cada vez que se agrega una variante.
- Cuando se quiere poder agregar variantes nuevas sin modificar el código existente.
- Cuando el algoritmo debe poder cambiarse en tiempo de ejecución o en tiempo de configuración.

---

### Ventajas y desventajas

| Ventajas | Desventajas |
|---|---|
| Cumple Open/Closed: agregar variante = agregar clase | Agrega más clases al proyecto |
| Elimina bloques `if/elif` en el Context | El cliente debe conocer las estrategias disponibles |
| Cada algoritmo vive aislado y es testeable por separado | Puede ser excesivo si solo hay dos variantes simples |
| El Context y las Strategies evolucionan independientemente | |

---

## 2. Aplicación en este proyecto — Caso de uso 2: Autenticación por rol

### El problema actual

En `presentation/views/auth_view.py` el comportamiento varía por rol del usuario
en **tres funciones distintas** con el mismo `if/elif`:

```python
# _procesar_login
if rol == "docente":
    resultado = auth_business.login_docente(email, password)
    destino = "/docente/inicio"
elif rol == "estudiante":
    resultado = auth_business.login_estudiante(email, password)
    destino = "/estudiante/inicio"

# _procesar_registro_docente  →  lógica exclusiva de docente
# _procesar_registro_estudiante  →  lógica exclusiva de estudiante
```

Lo que varía por rol es exactamente la misma familia de decisiones:

| Decisión | Docente | Estudiante |
|---|---|---|
| Método de login | `login_docente()` | `login_estudiante()` |
| Método de registro | `registrar_docente()` | `registrar_estudiante()` |
| Dashboard de destino | `/docente/inicio` | `/estudiante/inicio` |
| Template de registro | `registro_docente.html` | `registro_estudiante.html` |
| Campos del formulario | nombre, email, password, profesión | nombre, email, password |

Agregar un rol nuevo (Administrador, Coordinador) obliga a tocar `auth_view.py`
en varios puntos, arriesgando romper el flujo de los roles existentes.

---

### Diagrama de diseño procedimental — Estado actual (el problema)

Flujo interno de `_procesar_login` tal como existe hoy. Cada rol agrega un nuevo
rombo de decisión y una nueva rama, haciendo el procedimiento más difícil de mantener
con cada rol que se incorpore.

```mermaid
flowchart TD
    A([Inicio]) --> B[/Leer formulario:\nrol, email, password/]
    B --> C{¿rol ==\ndocente?}

    C -- Sí --> D[login_docente\nemail, password]
    D --> E[destino =\n/docente/inicio]

    C -- No --> F{¿rol ==\nestudiante?}
    F -- Sí --> G[login_estudiante\nemail, password]
    G --> H[destino =\n/estudiante/inicio]

    F -- No --> I[/Mostrar error:\nSelecciona un rol válido/]
    I --> Z([Fin])

    E --> J[Escribir cookie JWT]
    H --> J
    J --> K[Redirigir a destino]
    K --> Z
```

> Agregar un rol **Admin** signi fica añadir otro rombo debajo de `¿rol == estudiante?`,
> modificando un procedimiento que ya funciona y arriesgando romper los roles existentes.

---

### Diagrama de diseño procedimental — Con Strategy (la solución)

Con el patrón aplicado, `_procesar_login` deja de tomar decisiones sobre roles.
Solo busca la estrategia en un diccionario y le delega el trabajo. El procedimiento
no cambia aunque se agreguen diez roles nuevos.

```mermaid
flowchart TD
    A([Inicio]) --> B[/Leer formulario:\nrol, email, password/]
    B --> C[estrategia =\n_estrategias.get rol]
    C --> D{¿estrategia\nexiste?}

    D -- No --> E[/Mostrar error:\nRol no válido/]
    E --> Z([Fin])

    D -- Sí --> F[estrategia.login\nemail, password]
    F --> G[destino =\nestrategia.get_dashboard_url]
    G --> H[Escribir cookie JWT]
    H --> I[Redirigir a destino]
    I --> Z
```

> Agregar un rol **Admin** significa crear `AdminStrategy` y registrarla en el diccionario.
> Este procedimiento no se toca.

---

### Solución con Strategy

Cada rol se convierte en una **ConcreteStrategy** que encapsula todas sus decisiones.
`auth_view.py` pasa a ser el **Context**: recibe el rol como string, busca la estrategia
correspondiente en un diccionario y le delega todo el trabajo.

Agregar un rol nuevo = agregar una clase nueva + registrarla en el diccionario.
El resto del código no cambia.

---

### Diagrama de clases — Implementación específica

```mermaid
classDiagram
    class RolStrategy {
        <<interface>>
        +login(email: str, password: str) dict
        +registrar(body: dict) dict
        +get_dashboard_url() str
        +get_template_registro() str
        +extraer_datos_registro(body: dict) dict
    }

    class DocenteStrategy {
        -auth_business : AuthBusiness
        +login(email, password) dict
        +registrar(body) dict
        +get_dashboard_url() str
        +get_template_registro() str
        +extraer_datos_registro(body) dict
    }

    class EstudianteStrategy {
        -auth_business : AuthBusiness
        +login(email, password) dict
        +registrar(body) dict
        +get_dashboard_url() str
        +get_template_registro() str
        +extraer_datos_registro(body) dict
    }

    class AdminStrategy {
        -auth_business : AuthBusiness
        +login(email, password) dict
        +registrar(body) dict
        +get_dashboard_url() str
        +get_template_registro() str
        +extraer_datos_registro(body) dict
    }

    class AuthView {
        -_estrategias : dict
        +handle_auth_web(handler, method, partes)
        -_procesar_login(handler)
        -_procesar_registro(handler, rol)
        -_mostrar_registro(handler, rol)
    }

    class AuthBusiness {
        +login_docente(email, password) dict
        +login_estudiante(email, password) dict
        +registrar_docente(nombre, email, password, profesion) dict
        +registrar_estudiante(nombre, email, password) dict
    }

    AuthView o--> RolStrategy : delega en estrategia activa
    DocenteStrategy ..|> RolStrategy : implementa
    EstudianteStrategy ..|> RolStrategy : implementa
    AdminStrategy ..|> RolStrategy : implementa (futuro)
    DocenteStrategy --> AuthBusiness : usa
    EstudianteStrategy --> AuthBusiness : usa
    AdminStrategy --> AuthBusiness : usa
```

---

### Diagrama de secuencia — Flujo de login web

```mermaid
sequenceDiagram
    actor Browser
    participant AuthView
    participant RolStrategy
    participant AuthBusiness

    Browser->>AuthView: POST /login (rol=docente, email, password)

    AuthView->>AuthView: estrategia = _estrategias["docente"]

    AuthView->>RolStrategy: login(email, password)
    RolStrategy->>AuthBusiness: login_docente(email, password)
    AuthBusiness-->>RolStrategy: {token, docente}
    RolStrategy-->>AuthView: {token, docente}

    AuthView->>RolStrategy: get_dashboard_url()
    RolStrategy-->>AuthView: "/docente/inicio"

    AuthView-->>Browser: 302 → /docente/inicio + Set-Cookie: session=JWT

    Note over AuthView,RolStrategy: AuthView nunca llama directamente<br/>a login_docente() ni login_estudiante().<br/>Solo habla con la Strategy.
```

---

### Diagrama de secuencia — Flujo de registro web

```mermaid
sequenceDiagram
    actor Browser
    participant AuthView
    participant RolStrategy
    participant AuthBusiness

    Browser->>AuthView: POST /registro/docente (nombre, email, password, profesion)

    AuthView->>AuthView: estrategia = _estrategias["docente"]

    AuthView->>RolStrategy: extraer_datos_registro(body)
    RolStrategy-->>AuthView: {nombre, email, password, profesion}

    AuthView->>RolStrategy: registrar(body)
    RolStrategy->>AuthBusiness: registrar_docente(nombre, email, password, profesion)
    AuthBusiness-->>RolStrategy: {token, docente}
    RolStrategy-->>AuthView: {token, docente}

    AuthView->>RolStrategy: get_dashboard_url()
    RolStrategy-->>AuthView: "/docente/inicio"

    AuthView-->>Browser: 302 → /docente/inicio + Set-Cookie: session=JWT
```

---

### Ubicación de los archivos en el proyecto

```
presentation/
├── strategies/                       ← NUEVA carpeta
│   ├── __init__.py
│   ├── rol_strategy.py               ← interfaz base (RolStrategy)
│   ├── docente_strategy.py           ← DocenteStrategy
│   └── estudiante_strategy.py        ← EstudianteStrategy
├── views/
│   └── auth_view.py                  ← Context (se simplifica)
└── ...
```

---

### Extensibilidad — agregar un rol nuevo

Para agregar un rol **Administrador** con su propio portal `/admin/panel`:

1. Crear `presentation/strategies/admin_strategy.py` con clase `AdminStrategy`.
2. Registrarla en el diccionario de `auth_view.py`:

```python
_estrategias = {
    "docente":     DocenteStrategy(),
    "estudiante":  EstudianteStrategy(),
    "admin":       AdminStrategy(),   # ← única línea que cambia en AuthView
}
```

3. Crear la vista `presentation/views/admin_view.py`.
4. Agregar la ruta en `presentation/router.py`.

**Ninguna estrategia existente se toca.** El principio Open/Closed se cumple completamente.

---

## 3. Flujo completo de una petición HTTP

### Flujo general — cualquier ruta

Desde que el browser envía la petición hasta que recibe la respuesta, la petición
atraviesa cuatro capas. Cada capa tiene una responsabilidad única y no conoce los
detalles internos de la siguiente.

```mermaid
flowchart TD
    Browser(["🌐 Browser"])
    Browser -->|"HTTP Request\nGET /docente/inicio"| A

    subgraph main.py ["main.py — Entry point"]
        A["HTTPServer\nrecibe la conexión TCP"]
        A --> B["RequestHandler\ndo_GET / do_POST / ..."]
        B --> C["_despachar(method)\nenrutar(self, method, path)"]
    end

    C --> D

    subgraph router ["presentation/router.py — Enrutador"]
        D["enrutar()\nparsea la URL"]
        D --> E{"primera parte\nde la ruta"}
        E -->|"login / logout\nregistro"| F["handle_auth_web()"]
        E -->|"docente"| G["handle_docente_web()"]
        E -->|"estudiante"| H["handle_estudiante_web()"]
        E -->|"admin"| I["handle_admin_web()"]
        E -->|"static"| J["serve_static()"]
    end

    G --> MW

    subgraph middleware ["presentation/middlewares/auth_middleware.py"]
        MW["solo_docente_web()\nlee Cookie: session=JWT\nverifica el token"]
    end

    MW -->|"payload válido"| V

    subgraph views ["presentation/views/docente_view.py"]
        V["_inicio(handler, payload)\nllama al business"]
    end

    V --> BL

    subgraph business ["business/"]
        BL["MateriaBusiness / GrupoBusiness\nlógica de dominio"]
    end

    BL --> REPO

    subgraph data ["data/repositories/"]
        REPO["Repository\nejecutá el SQL\nvía psycopg2"]
        REPO <-->|"query / rows"| DB[("PostgreSQL")]
    end

    REPO --> BL
    BL --> V

    V --> RESP

    subgraph helpers ["utils/http_helpers.py"]
        RESP["render_template()\nsend_html(200, html)"]
    end

    RESP -->|"HTTP 200 + HTML"| Browser
    MW -->|"token inválido\nHTTP 302"| Browser
```

---

### Flujo específico — POST /login con el patrón Strategy

Este flujo muestra con detalle qué sucede cuando el usuario envía el formulario de
login. Es el recorrido que aplica el patrón Estrategia.

```mermaid
flowchart TD
    Browser(["🌐 Browser"])
    Browser -->|"POST /login\nrol=docente\nemail, password"| A

    subgraph main.py ["main.py"]
        A["RequestHandler.do_POST\n_despachar('POST')"]
    end

    A -->|"enrutar()"| B

    subgraph router ["router.py"]
        B["primera == 'login'\nhandle_auth_web(handler, 'POST', ['login'])"]
    end

    B --> C

    subgraph auth_view ["presentation/views/auth_view.py — Context"]
        C["_procesar_login(handler)\nlee el formulario con read_form_body()"]
        C --> D["_estrategias.get('docente')"]
        D --> E{"¿estrategia\nexiste?"}
        E -->|"No"| ERR1["render_template login.html\nerror='Rol no válido'\nsend_html 400"]
        E -->|"Sí"| F["estrategia.login(email, password)"]
    end

    F --> G

    subgraph strategy ["presentation/strategies/docente_strategy.py — ConcreteStrategy"]
        G["DocenteStrategy.login()\nllama al business"]
    end

    G --> H

    subgraph business ["business/auth_business.py"]
        H["login_docente(email, password)\nvalida campos"]
        H --> I["docente_repo.buscar_por_email()"]
        I --> J{"¿existe\ny bcrypt ok?"}
        J -->|"No"| ERR2["raise PermissionError\n'Credenciales incorrectas'"]
        J -->|"Sí"| K["generar_token()\n{sub, rol, nombre}"]
        K --> L["return {token, docente}"]
    end

    subgraph data ["data/repositories/docente_repository.py"]
        I <-->|"SELECT * FROM docente\nWHERE email = %s"| DB[("PostgreSQL")]
    end

    L --> G
    G -->|"resultado"| F
    F --> M

    subgraph auth_view2 ["auth_view.py — Context (continúa)"]
        M["token = resultado['token']\ndestino = estrategia.get_dashboard_url()\n→ '/docente/inicio'"]
        M --> N["send_response(302)\nLocation: /docente/inicio\nSet-Cookie: session=JWT; HttpOnly"]
    end

    ERR2 -->|"capturado en auth_view"| ERR3["render_template login.html\nerror=str(e)\nsend_html 400"]

    N -->|"HTTP 302 + cookie"| Browser
    ERR1 -->|"HTTP 400"| Browser
    ERR3 -->|"HTTP 400"| Browser
```

---

### Resumen por capa

| Capa | Archivo | Responsabilidad |
|---|---|---|
| **Entry point** | `main.py` | Recibe la conexión TCP, crea el handler, llama al router |
| **Router** | `presentation/router.py` | Parsea la URL y despacha al view correcto |
| **Middleware** | `auth_middleware.py` | Verifica el JWT de la cookie antes de permitir el acceso |
| **View / Context** | `presentation/views/*.py` | Lee el formulario, delega en la Strategy, construye la respuesta |
| **Strategy** | `presentation/strategies/*.py` | Encapsula las decisiones específicas de cada rol |
| **Business** | `business/*.py` | Valida reglas de dominio, hashea passwords, genera tokens |
| **Repository** | `data/repositories/*.py` | Ejecuta el SQL y mapea las filas a diccionarios |
| **DB** | PostgreSQL | Persiste y consulta los datos |
| **Helpers** | `utils/http_helpers.py` | Renderiza templates Jinja2 y escribe la respuesta HTTP |
