# Git Flow y GitHub

El remoto configurado es `https://github.com/Pafuna08/device_systems.git`.

## Flujo de la guia 8

```bash
git switch main
git pull origin main
git switch -c feature/crud-users
git add app requirements.txt
git commit -m "feat: implementar CRUD y capas de usuarios"
git add README.md QUICKSTART.md INICIO_RAPIDO.md RESUMEN_PROYECTO.md GITHUB_SETUP.md
git commit -m "docs: actualizar documentacion de la guia intermedia"
git push -u origin feature/crud-users
```

En GitHub se crea un Pull Request de `feature/crud-users` hacia `main`. Tras revisar las pruebas, se hace merge y se sincroniza:

```bash
git switch main
git pull origin main
git branch -d feature/crud-users
git push origin --delete feature/crud-users
```

## Convenciones

- `feat:` funcionalidad nueva.
- `fix:` correccion.
- `docs:` documentacion.
- `test:` pruebas.
- `chore:` configuracion.

No se deben subir `venv/`, tokens ni archivos `.env`. El `.gitignore` ya excluye el entorno virtual.