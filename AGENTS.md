# AGENTS.md - Guía rápida para agentes IA

Este archivo define cómo trabajar en `python-multigit` de forma segura, útil y consistente.

## 1) Objetivo del proyecto
`multigit` gestiona múltiples repositorios Git declarados en un archivo YAML llamado `subrepos`, procesándolos de forma recursiva desde un directorio base.

Piezas clave:
- CLI: `src/multigit/__main__.py`
- Orquestación recursiva: `src/multigit/subrepos.py`
- Operaciones Git por repositorio: `src/multigit/gitrepo.py`
- Carga/validación YAML: `src/multigit/subrepofile.py`

## 2) Fuente de verdad funcional
Antes de cambiar comportamiento, alinear siempre con:
- `README.md` para experiencia de usuario, semántica de `subrepos` y expectativas de uso.
- `Makefile` para flujo oficial de desarrollo (`test`, `build`, `doc`, `clean`, `upload*`).
- `pyproject.toml` para empaquetado, dependencias, script de entrada y build backend.

Requisito explícito de construcción:
- El backend de build es `hatchling.build` (vía Hatch). No introducir cambios que lo sustituyan o desalineen sin requerimiento explícito.

## 3) Comandos oficiales de desarrollo
Desde la raíz del repositorio:

```bash
make test
make build
make doc
make clean
```

Notas:
- `make test` usa `unittest discover` sobre `src/tests`.
- `make build` depende de `test`.
- `make clean` elimina también rutas potencialmente sensibles; revisa bien su impacto antes de ejecutarlo en contextos no aislados.

## 4) Restricciones que el agente debe respetar
- No romper la interfaz de línea de comandos (`multigit --run`, `multigit --status`, `-V`, `-h`).
- Mantener compatibilidad con la estructura YAML de `subrepos`.
- No introducir frameworks de test nuevos sin necesidad clara (hoy se usa `unittest`).
- No convertir rutas relativas de configuración en rutas con semántica distinta a la actual.
- Evitar cambios masivos de estilo no funcionales.
- Mantener la documentación Sphinx como parte del entregable cuando un cambio lo requiera.
- Respetar la estructura de documentación bajo `src/sphinx` y su flujo de generación/publicación.
- Al añadir o editar comentarios/docstrings en Python, usar sintaxis compatible con Sphinx (estilo reStructuredText cuando aplique).

## 5) Riesgos reales observados en la suite
La suite en `src/tests` es de tipo integración en varios casos:
- Usa repos remotos reales (`git@github.com:...`).
- Requiere conectividad y claves SSH válidas para varios tests.
- Un test hace `push`/`delete` de rama remota (`test_remote_operations.py`), por lo que puede fallar por permisos.

Al reportar resultados de test, distinguir siempre:
1. Fallo lógico del código.
2. Fallo de entorno/red/permisos remotos.

## 6) Checklist mínimo antes de dar un cambio por bueno
1. Ejecutar `make test` y registrar resultado.
2. Revisar que el flujo CLI siga funcionando con `--help` y `--version`.
3. Confirmar que no se alteró involuntariamente el contrato del archivo `subrepos`.
4. Si hay cambios en build o dependencias, validar consistencia con `pyproject.toml` y `Makefile`.
5. Documentar brevemente impacto funcional y riesgos residuales.
6. Si el cambio afecta documentación o API pública, actualizar contenidos en `src/sphinx` y validar `make doc`.

## 7) Qué debe incluir una entrega del agente
- Resumen corto de cambios funcionales.
- Archivos modificados y razón de cada cambio.
- Resultado de pruebas ejecutadas.
- Riesgos/limitaciones pendientes.
- Siguientes pasos concretos, si aplica.
