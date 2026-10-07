#!/usr/bin/env python3
"""Cifra a documentação (docs/) e grava site/docs/conteudo.bin para o GitHub Pages.

Uso:
    pip install cryptography
    BEEBIP_DOCS_PASSWORD='a-senha' python3 tools/build_site.py [pasta_docs]

A pasta docs/ (texto claro) NÃO vai para o repositório: fica só na máquina de quem gera.
Formato de conteudo.bin: "BBP1" + salt(16) + iv(12) + AES-256-GCM(gzip(html)).
Chave: PBKDF2-HMAC-SHA256, 600.000 iterações. A página site/docs/index.html faz o caminho inverso no navegador.
"""
import gzip, json, os, sys
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

RAIZ = Path(__file__).resolve().parent.parent
DOCS = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "docs"
SAIDA = RAIZ / "site" / "docs" / "conteudo.bin"
ITER = 600_000
ANEXOS = ["PRD.md", "SPEC.md", "BACKLOG.md", "backlog.csv"]

senha = os.environ.get("BEEBIP_DOCS_PASSWORD")
if not senha:
    sys.exit("Defina a variável de ambiente BEEBIP_DOCS_PASSWORD.")

html = (DOCS / "index.html").read_text(encoding="utf-8")
anexos = {n: (DOCS / n).read_text(encoding="utf-8-sig") for n in ANEXOS if (DOCS / n).exists()}

# Barra de arquivos e botão de sair, injetados na página já aberta.
barra = """
<style>
#bb-arq{position:fixed;right:16px;bottom:16px;z-index:50;font-family:inherit}
#bb-arq>button{border:2px solid #000;background:#000;color:#FFFDEA;border-radius:999px;padding:10px 18px;font:inherit;font-weight:600;font-size:14px;cursor:pointer}
#bb-arq .m{display:none;position:absolute;right:0;bottom:52px;background:#fff;border:2px solid #000;border-radius:16px;padding:8px;min-width:230px}
#bb-arq.on .m{display:block}
#bb-arq .m button{display:block;width:100%;text-align:left;border:0;background:none;padding:9px 12px;border-radius:10px;font:inherit;font-size:14.5px;cursor:pointer}
#bb-arq .m button:hover{background:#FFF1C2}
#bb-arq .m hr{border:0;border-top:1px solid #E6E1C3;margin:6px 0}
@media print{#bb-arq{display:none}}
</style>
<div id="bb-arq"><div class="m" role="menu"></div><button aria-haspopup="true" aria-expanded="false">Arquivos e sair</button></div>
<script id="bb-anexos" type="application/json">__ANEXOS__</script>
<script>
(() => {
  const A = JSON.parse(document.getElementById('bb-anexos').textContent), el = document.getElementById('bb-arq'), m = el.querySelector('.m'), bt = el.querySelector(':scope > button');
  const add = (t, f) => { const b = document.createElement('button'); b.textContent = t; b.setAttribute('role', 'menuitem'); b.onclick = f; m.appendChild(b) };
  for (const [nome, txt] of Object.entries(A)) add('Baixar ' + nome, () => {
    const u = URL.createObjectURL(new Blob([nome.endsWith('.csv') ? '\\ufeff' + txt : txt], {type: nome.endsWith('.csv') ? 'text/csv' : 'text/markdown'}));
    const a = Object.assign(document.createElement('a'), {href: u, download: nome}); document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(u), 2000) });
  m.appendChild(document.createElement('hr'));
  add('Página do projeto', () => { location.href = '../' });
  add('Sair (pedir senha de novo)', () => { try { sessionStorage.removeItem('beebip-docs') } catch {} location.reload() });
  bt.onclick = () => { const on = el.classList.toggle('on'); bt.setAttribute('aria-expanded', on) };
  document.addEventListener('click', e => { if (!el.contains(e.target)) { el.classList.remove('on'); bt.setAttribute('aria-expanded', false) } });
})();
</script>
""".replace("__ANEXOS__", json.dumps(anexos, ensure_ascii=False).replace("</", "<\\/"))

assert "</body>" in html
html = html.replace("</body>", barra + "</body>", 1)
html = html.replace("<head>", '<head>\n<meta name="robots" content="noindex, nofollow">\n<link rel="icon" href="../assets/icon.png">', 1)

claro = gzip.compress(html.encode("utf-8"), 9)
salt, iv = os.urandom(16), os.urandom(12)
chave = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(senha.encode("utf-8"))
SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_bytes(b"BBP1" + salt + iv + AESGCM(chave).encrypt(iv, claro, None))
print(f"ok: {SAIDA} ({SAIDA.stat().st_size / 1024:.0f} KB), anexos: {', '.join(anexos) or 'nenhum'}")
