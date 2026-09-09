# Git Flow y GitHub - EV09 SQLAlchemy

El remoto configurado es `https://github.com/Pafuna08/device_systems.git`.

## Flujo de la guia 9

```bash
git switch main
git pull origin main
git switch -c feature/sqlalchemy-persistence
git add app requirements.txt .gitignore
git commit -m "feat: configurar SQLite y modelo SQLAlchemy"
git add app/routes app/services app/dependencies
git commit -m "feat: migrar CRUD de usuarios a SQLAlchemy"
git add README.md QUICKSTART.md INICIO_RAPIDO.md RESUMEN_PROYECTO.md GITHUB_SETUP.md
git commit -m "docs: actualizar documentacion de la guia intermedia"
git push -u origin feature/sqlalchemy-persistence
```

Para completar las evidencias de persistencia se usa la misma rama:

```bash
git switch main
git pull origin main
git add README.md evidencias
git commit -m "docs: actualizar evidencias de persistencia"
git push -u origin feature/sqlalchemy-persistence
```

En GitHub se crea un Pull Request de `feature/sqlalchemy-persistence` hacia `main`. Tras revisar las pruebas, se fusiona y se sincroniza:

```bash
git switch main
git pull origin main
git branch -d feature/sqlalchemy-persistence
git push origin --delete feature/sqlalchemy-persistence
```

## Convenciones

- `feat:` funcionalidad nueva.
- `fix:` correccion.
- `docs:` documentacion.
- `test:` pruebas.
- `chore:` configuracion.

No se deben subir `venv/`, tokens ni archivos `.env`. El `.gitignore` ya excluye el entorno virtual.
