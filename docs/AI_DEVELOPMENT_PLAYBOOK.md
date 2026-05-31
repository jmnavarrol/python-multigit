# AI Development Playbook for python-multigit

## Propósito
Este documento está pensado para agentes de IA que vayan a modificar el repositorio `python-multigit` en futuras iteraciones. Su objetivo es reducir errores de contexto y acelerar cambios seguros.

## 1. Contexto técnico esencial

### 1.1 Entrada principal de la aplicación
- Script CLI: `src/multigit/__main__.py`
- Comportamientos principales:
  - `--run`: procesa subrepositorios y aplica cambios.
  - `--status`: solo reporta estado.
  - `--version` y `--help`: utilidades de CLI.

### 1.2 Núcleo de negocio
- `src/multigit/subrepos.py`
  - Localiza archivo `subrepos` en `base_path` o en el root del repo Git padre.
  - Carga definiciones con `Subrepofile`.
  - Recorre recursivamente subrepos y aplica `status()` o `update()` por cada uno.
  - Imprime estados enriquecidos para cada subrepo.

- `src/multigit/gitrepo.py`
  - `status(repoconf)`: clasifica cada sandbox en estados como:
    - `NOT_CLONED`, `ERROR`, `WRONG_REMOTE`, `EMPTY`, `DIRTY`, `PENDING_UPDATE`, `UP_TO_DATE`.
  - `update(repoconf)`: actúa según estado:
    - Clona (`CLONED`) si no existe.
    - Hace checkout/pull cuando hay `PENDING_UPDATE`.
    - Evita tocar repos con `DIRTY`, `WRONG_REMOTE`, `ERROR`, etc.

- `src/multigit/subrepofile.py`
  - Carga YAML con `yaml.safe_load`.
  - Valida con Cerberus usando `subrepos_schema.yaml`.
  - Normaliza:
    - `path` a ruta absoluta.
    - `gitref_type` en `branch|tag|commit|None`.

## 2. Archivo subrepos: contrato funcional

Tomando como referencia `README.md`:
- Clave raíz: `subrepos` (lista).
- Cada entrada requiere:
  - `repo`
  - `path`
- Opcionalmente, uno de:
  - `branch`
  - `tag`
  - `commit`

La semántica de orden importa: la lista se procesa en orden y eso habilita layouts jerárquicos.

## 3. Flujo de desarrollo oficial (derivado de Makefile)

Objetivos relevantes:
- `test`: `python -m unittest discover --start-directory ${SOURCE_DIR}tests`
- `build`: ejecuta `test`, luego construye `sdist` y `wheel` con Hatch, y documentación Sphinx.
- `doc`: genera docs HTML y linkcheck.
- `clean`: limpia artefactos de build y caches Python.

Implicaciones para agentes:
- Si cambias comportamiento, ejecuta siempre `make test`.
- Si cambias empaquetado, valida también `make build`.
- Revisa con cuidado `clean` porque borra rutas fuera de artefactos típicos.
- Si tocas documentación o contratos públicos, ejecuta también `make doc`.

Publicación/documentación:
- La documentación del proyecto se construye con Sphinx y se publica a partir de esos artefactos.
- Cualquier cambio funcional relevante debe evaluarse también desde su impacto en `src/sphinx`.

## 4. Packaging y dependencias (pyproject.toml)

- Proyecto: `multigit`
- Requiere Python `>=3.7`.
- Dependencias runtime:
  - `Cerberus`, `colorama`, `GitPython`, `PyYAML`
- Script instalado:
  - `multigit = multigit:__main__.main`
- Build backend:
  - `hatchling.build`
- Fuente de versión:
  - `tool.hatch.version.path = src/multigit/__main__.py`

Regla de seguridad para cambios:
- Si tocas versión, coherencia con changelog y proceso de publicación.
- Si tocas dependencias, justificar impacto en runtime o dev workflow.
- Si tocas build/packaging, mantener explícitamente el backend `hatchling.build` salvo requerimiento formal de migración.

## 4.1 Reglas de documentación Sphinx para agentes

- Estructurar y mantener contenidos bajo `src/sphinx` (índices, páginas y referencias) sin romper navegación existente.
- Mantener consistencia de estilo con reStructuredText en los archivos de documentación.
- Cuando se modifiquen docstrings/comentarios en código fuente Python y estos formen parte de documentación técnica, usar sintaxis compatible con Sphinx.
- Evitar comentarios ambiguos o de bajo valor; preferir descripciones técnicas claras, orientadas a API, parámetros, retornos y efectos colaterales.

## 5. Pruebas: cómo interpretarlas correctamente

Ubicación: `src/tests`

Características importantes:
- Framework actual: `unittest` (descubrimiento automático).
- Naturaleza: mezcla de unit/integration.
- Dependencias externas:
  - Varios tests dependen de repos reales en GitHub por SSH.
  - `test_remote_operations.py` incluye push/delete de rama remota, por lo que exige permisos en remoto.

Lectura de resultados:
- Si falla por `Permission denied`, `Repository not found`, timeout de red o SSH, probablemente es entorno.
- Si falla en comparación de estados esperados (`UP_TO_DATE`, `DIRTY`, etc.), probablemente es regresión funcional.

## 6. Guía de cambios por tipo de tarea

### 6.1 Cambios de CLI
1. Modificar `__main__.py`.
2. Verificar opciones excluyentes y mensajes de ayuda.
3. Ejecutar `make test`.
4. Actualizar README si cambia UX.
5. Evaluar impacto en documentación Sphinx (`src/sphinx`) y actualizar si aplica.

### 6.2 Cambios de parsing/validación YAML
1. Modificar `subrepofile.py` y, si aplica, `subrepos_schema.yaml`.
2. Asegurar que se conserva normalización de `path` y `gitref_type`.
3. Ejecutar `make test`.
4. Añadir/ajustar fixtures en `src/tests/helperfiles` si cambia contrato.
5. Actualizar documentación Sphinx y ejemplos si cambia el contrato de `subrepos`.

### 6.3 Cambios de lógica Git
1. Modificar `gitrepo.py` o `subrepos.py`.
2. Respetar estados existentes y su semántica.
3. Ejecutar `make test`.
4. Reportar explícitamente qué estados cambian y por qué.
5. Revisar docstrings/comentarios tocados para mantener compatibilidad con Sphinx.

## 7. Convenciones recomendadas para agentes IA

- Priorizar cambios mínimos y localizados.
- Preservar nombres de estados y comportamiento observable salvo requerimiento explícito.
- Evitar refactors de estilo junto a cambios funcionales.
- Documentar en el reporte final:
  1. Qué cambió.
  2. Por qué.
  3. Cómo se verificó.
  4. Qué queda pendiente.

## 8. Plantillas de prompt reutilizables para agentes

### 8.1 Fix funcional puntual
"Analiza el fallo en [archivo/test], aplica el cambio mínimo en `src/multigit`, ejecuta `make test`, y devuelve resumen con causa raíz, diff lógico y riesgos residuales."

### 8.2 Evolución de contrato subrepos
"Extiende el contrato de `subrepos` para soportar [nuevo campo], actualiza validación Cerberus y tests/fixtures asociados, manteniendo compatibilidad hacia atrás y reportando impacto en README y CLI."

### 8.3 Hardening de errores Git
"Refuerza manejo de errores en `gitrepo.py` para [caso], preserva semántica de estados existentes y añade cobertura de test sin introducir nuevas dependencias."

## 9. Observaciones de mantenimiento para backlog técnico

- Hay código de guardia `if __name__ == '__main__'` en algunos módulos no-CLI que referencia `main()` no definido; no suele afectar como librería, pero conviene saneamiento futuro.
- La suite depende de recursos remotos reales; considerar separar pruebas online/offline para CI robusta.
- Verificar y acotar el alcance real de `clean` si se usa en entornos con carpetas adyacentes relevantes.
