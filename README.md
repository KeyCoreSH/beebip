# BeeBip

Plataforma de transporte escolar que conecta famílias, motoristas e escolas: embarque confirmado, aviso na hora certa e gestão profissional para o motorista.

- **Página do projeto:** https://keycoresh.github.io/beebip/
- **Documentação (PRD, SPEC e backlog):** https://keycoresh.github.io/beebip/docs/ (acesso com senha, peça ao time)

## O que há neste repositório

| Caminho | Conteúdo |
|---|---|
| `site/index.html` | Página pública do projeto |
| `site/docs/index.html` | Porta de entrada da área restrita (pede a senha e abre o conteúdo no navegador) |
| `site/docs/conteudo.bin` | Documentação cifrada (AES-256-GCM, chave derivada da senha por PBKDF2-SHA256 com 600 mil iterações) |
| `tools/build_site.py` | Gera `conteudo.bin` a partir da pasta local `docs/` |

A documentação em texto claro (`docs/`) e os artefatos originais (`artefatos/`) **não são versionados aqui** (veja `.gitignore`). A senha também não fica no repositório.

## Atualizar a documentação publicada

```bash
pip install cryptography
BEEBIP_DOCS_PASSWORD='a-senha' python3 tools/build_site.py   # lê ./docs e grava site/docs/conteudo.bin
git add site && git commit -m "Atualiza documentação" && git push
git subtree push --prefix site origin gh-pages                # publica no GitHub Pages
```

## Sobre a proteção por senha

O GitHub Pages só serve arquivos estáticos, então a proteção é feita por criptografia no navegador: sem a senha, o conteúdo não abre. O arquivo cifrado é público, portanto a segurança depende da força da senha. Para trocar a senha, gere o conteúdo de novo com a senha nova e publique.
