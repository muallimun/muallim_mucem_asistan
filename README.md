# 📚 Muallimun Arapça Sözlük Asistanı v1.4.8

<p align="center">
  <img src="https://img.shields.io/badge/Versiyon-1.4.8-blue?style=for-the-badge" alt="Versiyon">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/Dil-Python%20%2F%20PyQt6-green?style=for-the-badge&logo=python" alt="Dil">
</p>

**Muallimun Arapça Sözlük Asistanı**, dijital metinler üzerinde çalışan eğitimciler, çevirmenler ve dil öğrencileri için geliştirilmiş, sistem genelinde (global) çalışan akıllı bir yardımcıdır. Sadece bir sözlük değil, kelime bankanızı oluşturan bir veri asistanıdır.

---

## 🛡️ Güvenlik Duyurusu ve Yanlış Alarm Bildirimi (Security Notice)

**⚠️ Neden Virüs Uyarısı Alıyorum?**
Uygulamamız Python diliyle geliştirilmiş açık kaynaklı ve güvenli bir projedir. Windows Defender veya tarayıcıların (Chrome/Edge) uyarı verme sebepleri şunlardır:
1. **Dijital İmza Eksikliği:** Uygulama, bireysel bir geliştirici projesi olduğu için maliyeti çok yüksek olan "Kod İmzalama Sertifikası"na henüz sahip değildir.
2. **Sistem Kancaları (Hooks):** Uygulama, kelime yakalamak için klavye ve fare hareketlerini takip eder. Antivirüs yazılımları bu fonksiyonu (keylogger şüphesiyle) yanlışlıkla tehdit olarak algılayabilir.
3. **Paketleme:** PyInstaller ile yapılan paketlemeler bazen antivirüs veritabanlarında hatalı eşleşmelere yol açar.

**Güvenle kullanabilirsiniz. İndirme ve kurulum sırasında çıkan uyarılarda "Sakla" ve "Yine de Çalıştır" seçeneklerini kullanarak devam edebilirsiniz.**

---

## 🔥 Neden Muallimun Asistan?

Geleneksel sözlüklerden farklı olarak bu uygulama, çalışma akışınızı bozmadan metinleri yakalar ve karmaşık Windows güvenlik kısıtlamalarını profesyonel çözümlerle aşar.

### ✨ Öne Çıkan Özellikler

* 🌍 **Evrensel Metin Yakalama:** PDF okuyucular (Acrobat vb.), Word belgeleri ve tüm web tarayıcılarında kesintisiz çalışır.
* 🤖 **Akıllı Dil Algılama (Smart Detect):** Seçtiğiniz kelimenin Arapça, Türkçe veya İngilizce olduğunu otomatik olarak algılar ve sizi en uygun sözlük moduna (AR-TR, EN-AR vb.) yönlendirir.
* 🛡️ **Sessiz Başlatma:** Windows başlangıcında onay kutusu (UAC) uyarısı çıkarmadan, Görev Zamanlayıcı aracılığıyla otomatik başlar.
* 🧹 **Reklamsız Deneyim:** Çeviri sonuçlarındaki dikkat dağıtıcı reklamları otomatik olarak temizler.
* 📊 **Dinamik Kelime Bankası:** Aradığınız kelimeleri tarih, saat ve anlam bilgisiyle birlikte kişisel Excel dosyanıza kaydeder.
* 🌐 **Çoklu Dil Arayüzü:** Türkçe, İngilizce ve Arapça dil desteği sunar.

---

## ⌨️ Kullanım Kısayolları

Uygulama, hız için iki farklı erişim yöntemi sunar:

| Yöntem | İşlem | Açıklama |
| :--- | :--- | :--- |
| **Fare (Önerilen)** | `Seç + Orta Tekerlek` | Metni seçip farenin orta tuşuna tıklayın. |
| **Klavye** | `Seç + Ctrl+Shift+Z` | Özelleştirilebilir global kısayol kombinasyonu. |

---

## 🚀 Kurulum Talimatları

1. **İndirme:** [Releases](https://github.com/muallimun/muallim_mucem_asistan/releases) sayfasından en güncel kurulum dosyasını indirin.
2. **Tarayıcı Onayı:** Chrome veya Edge "Tehlikeli olabilir" uyarısı verirse, üç noktaya (...) basıp **"Sakla"** (Keep) seçeneğini işaretleyin.
3. **Yine de Çalıştır:** Kurulumu başlatın; Windows SmartScreen uyarısı çıkarsa **"Ek Bilgi"** bağlantısına ve ardından **"Yine de Çalıştır"** butonuna basın.
4. **Önemli Ayar:** Kurulum bittikten sonra Ayarlar penceresinden "Windows açılışında otomatik başlat" seçeneğini **bir kez kapatıp tekrar aktif edin**. Bu, Windows başlangıç kayıtlarını güncelleyecektir.

---

## 🛠️ Teknik Altyapı

Uygulama modern kütüphaneler ve ileri seviye Windows entegrasyonu ile geliştirilmiştir:
* **Arayüz:** PyQt6 & QtWebEngine
* **Hook Mekanizması:** Keyboard & Mouse global listeners
* **Veri Yönetimi:** Openpyxl (Excel entegrasyonu)
* **Sistem:** Windows Task Scheduler API (Sessiz başlangıç yönetimi için)

---

## 📝 Lisans ve Destek

Bu proje **Muallimun.Net** tarafından dil eğitimine katkı amacıyla geliştirilmiştir.

* **Geliştirici:** Muallimun Ekibi
* **İletişim:** [tatabdullah@hotmail.com](mailto:tatabdullah@hotmail.com)
* **Web:** [muallimun.net](https://www.muallimun.net)

---
<p align="center"><i>Arapça öğrenim sürecinizi hızlandırmak için tasarlandı.</i></p>