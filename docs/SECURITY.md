# Güvenlik ve Sır (Secret) Yönetimi

Bu proje için sır yönetimini sıkı tutmak üzere aşağıdaki kurallar geçerlidir:

- Sırları (token, API key, şifre, cookie, access token) asla repoya koyma — yorum satırı dahi olsa.
- Tüm sırlar `.env` gibi git-ignored dosyalarda veya CI/CD gizli değişkenlerinde tutulur.
- Örnek/şablon olarak `.env.example` kullanılır; gerçek değerler eklenmez.
- Git geçmişinde sızıntı tespit edilirse anahtar hemen revoke/rotate edilir ve geçmiş `git-filter-repo` ile temizlenir.

## Otomatik Koruma

- Pre-commit: `gitleaks` staged değişikliklerde secret taraması yapar.
- CI: GitHub Actions üzerinden her push/PR için `gitleaks` taraması çalışır.
- GitHub Push Protection: Repo ayarlarında açıksa, GitHub kendisi de push anında bloklayabilir.

## Kurulum (Geliştirici Makinesinde)

```powershell
# pre-commit kur
pip install pre-commit

# hook'ları aktif et
pre-commit install

# ilk tarama (opsiyonel)
pre-commit run --all-files
```

## Manuel Tarama

```powershell
# gitleaks yoksa yükle (Windows için choco örneği)
choco install gitleaks -y

# çalışma ağacını tara
gitleaks detect --source . --no-git -v

# tüm git geçmişini tara
gitleaks detect --source . -v
```

## Temizlik (Geçmişte Sızıntı Varsa)

1. İlgili anahtarı sağlayıcısından derhal revoke/rotate et.
2. Dosyadan tamamen kaldır.
3. `git-filter-repo` ile tüm geçmişteki izleri sil ve force push et.

```powershell
pip install --user git-filter-repo
# örnek replace-text kullanımı
"LEAKED_TOKEN==>[REMOVED]" | Out-File -Encoding utf8 replacements.txt
& "$env:APPDATA\Python\Python*\Scripts\git-filter-repo.exe" --force --replace-text replacements.txt

git push -u origin main --force-with-lease
```

## Sık Karşılaşılan Desenler
- `ghp_`, `github_pat_`, `gsk_`, `sk-` ile başlayan anahtarlar
- `Authorization: Bearer <...>` başlıkları
- `BEGIN PRIVATE KEY` blokları

Her şüpheli durumda commit etmeden önce pre-commit taraması çalıştır ve hatayı düzeltmeden commit etme.